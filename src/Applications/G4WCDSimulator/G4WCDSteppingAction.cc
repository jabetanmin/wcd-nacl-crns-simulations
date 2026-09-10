// Registro de informacion paso a paso del modelo WCD.

#include "G4WCDSteppingAction.h"

#include "G4AutoLock.hh"
#include "G4DynamicParticle.hh"
#include "G4Element.hh"
#include "G4Event.hh"
#include "G4Exception.hh"
#include "G4HadronicProcess.hh"
#include "G4Material.hh"
#include "G4Nucleus.hh"
#include "G4OpticalPhoton.hh"
#include "G4ParticleDefinition.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4Step.hh"
#include "G4StepPoint.hh"
#include "G4SystemOfUnits.hh"
#include "G4Track.hh"
#include "G4VProcess.hh"

#include <fstream>
#include <iomanip>
#include <sstream>
#include <string>
#include <vector>

namespace
{
G4Mutex outputMutex = G4MUTEX_INITIALIZER;

const G4String outputDirectory = "Datos-simulacion/";

const char* stepHeader =
  "# run_id\tevent_id\tparticle\ttrack_id\tparent_id\tstep_number\t"
  "creator_process\tstep_process\tmaterial\tpre_x_cm\tpre_y_cm\tpre_z_cm\t"
  "post_x_cm\tpost_y_cm\tpost_z_cm\tpre_energy_MeV\tpost_energy_MeV\t"
  "global_time_ns";

const char* secondaryHeader =
  "# run_id\tevent_id\tcategory\tparent_particle\tparent_track_id\t"
  "parent_step_number\tsecondary_index\tparticle\ttrack_id\tparent_id\t"
  "creator_process\tmaterial\tx_cm\ty_cm\tz_cm\tkinetic_energy_MeV\t"
  "global_time_ns";

const char* captureHeader =
  "# run_id\tevent_id\tparticle\ttrack_id\tparent_id\tstep_number\t"
  "step_process\tmaterial\ttarget_Z\ttarget_A\tpre_x_cm\tpre_y_cm\tpre_z_cm\t"
  "post_x_cm\tpost_y_cm\tpost_z_cm\tpre_energy_MeV\tpost_energy_MeV\t"
  "global_time_ns";

G4String ProcessName(const G4VProcess* process)
{
  return process ? process->GetProcessName() : "none";
}

G4String MaterialName(const G4StepPoint* point)
{
  return (point && point->GetMaterial()) ? point->GetMaterial()->GetName()
                                         : "none";
}

G4int CurrentRunId()
{
  const auto* runManager = G4RunManager::GetRunManager();
  const auto* run = runManager ? runManager->GetCurrentRun() : nullptr;
  return run ? run->GetRunID() : -1;
}

G4int CurrentEventId()
{
  const auto* runManager = G4RunManager::GetRunManager();
  const auto* event = runManager ? runManager->GetCurrentEvent() : nullptr;
  return event ? event->GetEventID() : -1;
}

// Agrega una linea TSV de forma segura en ejecuciones multihilo. El encabezado
// se escribe una sola vez cuando el archivo no existe o esta vacio.
void AppendTsv(const G4String& fileName,
               const char* header,
               const G4String& row)
{
  G4AutoLock lock(&outputMutex);

  const G4String path = outputDirectory + fileName;
  std::ifstream input(path.c_str(), std::ios::binary | std::ios::ate);
  const bool needsHeader = !input.good() || input.tellg() == std::streampos(0);
  input.close();

  std::ofstream output(path.c_str(), std::ios::out | std::ios::app);
  if (!output) {
    G4ExceptionDescription description;
    description << "No se pudo abrir " << path
                << ". Compruebe que el directorio Datos-simulacion existe "
                << "y tiene permisos de escritura.";
    G4Exception("AppendTsv", "WCD-OUTPUT-001", FatalException, description);
    return;
  }

  if (needsHeader) {
    output << header << '\n';
  }
  output << row << '\n';
}

G4String StepRow(const G4Step* step, const G4String& processName)
{
  const auto* track = step->GetTrack();
  const auto* pre = step->GetPreStepPoint();
  const auto* post = step->GetPostStepPoint();
  const auto prePosition = pre->GetPosition();
  const auto postPosition = post->GetPosition();

  std::ostringstream row;
  row << std::setprecision(10)
      << CurrentRunId() << '\t'
      << CurrentEventId() << '\t'
      << track->GetParticleDefinition()->GetParticleName() << '\t'
      << track->GetTrackID() << '\t'
      << track->GetParentID() << '\t'
      << track->GetCurrentStepNumber() << '\t'
      << ProcessName(track->GetCreatorProcess()) << '\t'
      << processName << '\t'
      << MaterialName(pre) << '\t'
      << prePosition.x() / cm << '\t'
      << prePosition.y() / cm << '\t'
      << prePosition.z() / cm << '\t'
      << postPosition.x() / cm << '\t'
      << postPosition.y() / cm << '\t'
      << postPosition.z() / cm << '\t'
      << pre->GetKineticEnergy() / MeV << '\t'
      << post->GetKineticEnergy() / MeV << '\t'
      << track->GetGlobalTime() / ns;
  return row.str();
}

void WriteSecondaries(const G4Step* step,
                      const G4String& category,
                      const G4String& fileName)
{
  const auto* parent = step->GetTrack();
  const auto* pre = step->GetPreStepPoint();
  const auto* secondaries = step->GetSecondaryInCurrentStep();

  for (std::size_t index = 0; index < secondaries->size(); ++index) {
    const auto* secondary = (*secondaries)[index];
    const auto position = secondary->GetPosition();

    std::ostringstream row;
    row << std::setprecision(10)
        << CurrentRunId() << '\t'
        << CurrentEventId() << '\t'
        << category << '\t'
        << parent->GetParticleDefinition()->GetParticleName() << '\t'
        << parent->GetTrackID() << '\t'
        << parent->GetCurrentStepNumber() << '\t'
        << index << '\t'
        << secondary->GetParticleDefinition()->GetParticleName() << '\t'
        << secondary->GetTrackID() << '\t'
        << secondary->GetParentID() << '\t'
        << ProcessName(secondary->GetCreatorProcess()) << '\t'
        << MaterialName(pre) << '\t'
        << position.x() / cm << '\t'
        << position.y() / cm << '\t'
        << position.z() / cm << '\t'
        << secondary->GetKineticEnergy() / MeV << '\t'
        << secondary->GetGlobalTime() / ns;

    AppendTsv(fileName, secondaryHeader, row.str());
  }
}

void WriteCapture(const G4Step* step, const G4String& processName)
{
  const auto* track = step->GetTrack();
  const auto* pre = step->GetPreStepPoint();
  const auto* post = step->GetPostStepPoint();
  const auto prePosition = pre->GetPosition();
  const auto postPosition = post->GetPosition();

  G4int targetZ = -1;
  G4int targetA = -1;
  const auto* process = post->GetProcessDefinedStep();
  const auto* hadronicProcess = dynamic_cast<const G4HadronicProcess*>(process);
  if (hadronicProcess && hadronicProcess->GetTargetNucleus()) {
    targetZ = hadronicProcess->GetTargetNucleus()->GetZ_asInt();
    targetA = hadronicProcess->GetTargetNucleus()->GetA_asInt();
  }

  std::ostringstream row;
  row << std::setprecision(10)
      << CurrentRunId() << '\t'
      << CurrentEventId() << '\t'
      << track->GetParticleDefinition()->GetParticleName() << '\t'
      << track->GetTrackID() << '\t'
      << track->GetParentID() << '\t'
      << track->GetCurrentStepNumber() << '\t'
      << processName << '\t'
      << MaterialName(pre) << '\t'
      << targetZ << '\t'
      << targetA << '\t'
      << prePosition.x() / cm << '\t'
      << prePosition.y() / cm << '\t'
      << prePosition.z() / cm << '\t'
      << postPosition.x() / cm << '\t'
      << postPosition.y() / cm << '\t'
      << postPosition.z() / cm << '\t'
      << pre->GetKineticEnergy() / MeV << '\t'
      << post->GetKineticEnergy() / MeV << '\t'
      << track->GetGlobalTime() / ns;

  AppendTsv("capturas-neutrones.tsv", captureHeader, row.str());
}

bool IsGammaInteraction(const G4String& processName)
{
  return processName == "phot" || processName == "compt" ||
         processName == "conv" || processName == "Rayl";
}

bool IsNeutronInteraction(const G4String& processName)
{
  return processName == "hadElastic" || processName == "nCapture" ||
         processName == "neutronInelastic";
}

void WriteCerenkovPhotons(const G4Step* step)
{
  const auto* parent = step->GetTrack();
  const auto* pre = step->GetPreStepPoint();
  const auto* secondaries = step->GetSecondaryInCurrentStep();

  for (std::size_t index = 0; index < secondaries->size(); ++index) {
    const auto* secondary = (*secondaries)[index];
    const auto* creator = secondary->GetCreatorProcess();

    if (secondary->GetParticleDefinition() != G4OpticalPhoton::Definition() ||
        ProcessName(creator) != "Cerenkov") {
      continue;
    }

    const auto position = secondary->GetPosition();
    std::ostringstream row;
    row << std::setprecision(10)
        << CurrentRunId() << '\t'
        << CurrentEventId() << '\t'
        << "Cerenkov" << '\t'
        << parent->GetParticleDefinition()->GetParticleName() << '\t'
        << parent->GetTrackID() << '\t'
        << parent->GetCurrentStepNumber() << '\t'
        << index << '\t'
        << secondary->GetParticleDefinition()->GetParticleName() << '\t'
        << secondary->GetTrackID() << '\t'
        << secondary->GetParentID() << '\t'
        << ProcessName(creator) << '\t'
        << MaterialName(pre) << '\t'
        << position.x() / cm << '\t'
        << position.y() / cm << '\t'
        << position.z() / cm << '\t'
        << secondary->GetKineticEnergy() / MeV << '\t'
        << secondary->GetGlobalTime() / ns;

    AppendTsv("fotones-cherenkov.tsv", secondaryHeader, row.str());
  }
}
}  // namespace

G4WCDSteppingAction::G4WCDSteppingAction(
  const G4WCDConstruction* detector,
  G4WCDEventAction* eventAction,
  Event& event)
  : G4UserSteppingAction(),
    fDetectorConstruction(detector),
    fEventAction(eventAction),
    fEvent(event)
{}

void G4WCDSteppingAction::UserSteppingAction(const G4Step* step)
{
  if (!step || !step->GetTrack() || !step->GetPreStepPoint() ||
      !step->GetPostStepPoint()) {
    return;
  }

  const auto* track = step->GetTrack();
  const G4String particleName =
    track->GetParticleDefinition()->GetParticleName();
  const G4String processName =
    ProcessName(step->GetPostStepPoint()->GetProcessDefinedStep());
  const G4String row = StepRow(step, processName);

  // Historia completa. Puede generar archivos grandes; comentese esta linea
  // cuando solo se necesiten los productos filtrados.
  AppendTsv("pasos-particulas.tsv", stepHeader, row);

  if (particleName == "neutron") {
    AppendTsv("pasos-neutrones.tsv", stepHeader, row);

    // Solo los neutrones primarios incidentes, no neutrones secundarios.
    if (track->GetParentID() == 0 && track->GetCurrentStepNumber() == 1) {
      AppendTsv("neutrones-incidentes.tsv", stepHeader, row);
    }

    if (IsNeutronInteraction(processName)) {
      AppendTsv("interacciones-neutrones.tsv", stepHeader, row);
    }

    if (processName == "nCapture") {
      WriteCapture(step, processName);
      WriteSecondaries(step,
                       "nCapture",
                       "secundarias-captura-neutron.tsv");
    } else if (processName == "neutronInelastic") {
      WriteSecondaries(step,
                       "neutronInelastic",
                       "secundarias-inelastica-neutron.tsv");
    }
  }

  if (particleName == "gamma") {
    AppendTsv("pasos-gamma.tsv", stepHeader, row);
    if (IsGammaInteraction(processName)) {
      AppendTsv("interacciones-gamma.tsv", stepHeader, row);
      WriteSecondaries(step,
                       processName,
                       "secundarias-interaccion-gamma.tsv");
    }
  }

  if (particleName == "e-" || particleName == "e+") {
    AppendTsv("pasos-electrones.tsv", stepHeader, row);
  }

  // Cerenkov se reconoce por el proceso creador del foton optico. No suele
  // ser el proceso que limita el paso de la particula cargada.
  WriteCerenkovPhotons(step);
}
