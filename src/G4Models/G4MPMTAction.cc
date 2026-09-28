#include "G4MPMTAction.h"
#include "SimData.h"
#include "DetectorSimData.h"
#include "OptDeviceSimData.h"
#include "OptDevice.h"
#include "CorsikaUtilities.h"

#include <G4Step.hh>
#include <G4TouchableHistory.hh>
#include <G4RunManager.hh>
#include <G4OpticalPhoton.hh>

using namespace std;

G4MPMTAction::G4MPMTAction(const G4String& name, const G4int dId, const G4int oId, Event& theEvent) :
		G4VSensitiveDetector(name),
		fEvent(theEvent),
		fDetectorId(dId),
		fOptDeviceId(oId)

	{ 
		
		cout << "[INFO] G4Models::G4MPMTAction: Registering Sensitive Detector " << name << endl;
		SimData& simData = fEvent.GetSimData();
		DetectorSimData& detSimData = simData.GetDetectorSimData(fDetectorId);
		detSimData.MakeOptDeviceSimData(fOptDeviceId);
		// OptDeviceSimData& OptDeviceSimData = detSimData.GetOptDeviceSimData(fOptDeviceId);

	}

void
G4MPMTAction::Initialize(G4HCofThisEvent* const /*hce*/)
{
	NumCerenkovPhotons = 0;
	NumPE = 0;
	NumPEMuDecay = 0;
	fPETime.clear();
	fPETimeComp.clear();
	fPETimeMuDecay.clear();
}

void
G4MPMTAction::EndOfEvent(G4HCofThisEvent* const /*hce*/)
{
	

	// gets current particle in the event to stream the number of PE for each particle
	Particle currentParticle = fEvent.GetSimData().GetCurrentParticle();
	int partId = currentParticle.GetParticleId();
	// time distribution for different particles

	Particle::Component particleComponent = currentParticle.GetComponent(/*particleType*/);

	DetectorSimData& detSimData = fEvent.GetSimData().GetDetectorSimData(fDetectorId);
	OptDeviceSimData& odSimData = detSimData.GetOptDeviceSimData(fOptDeviceId);
	int charge = fPETime.size();
	

        std::ofstream outputFilenum("Datos-simulacion/Carga-total.txt", std::ios_base::app);
        outputFilenum <<"Carga:" <<"\t"<< fPETime.size() <<"\n";

	std::ofstream outputFile("Datos-simulacion/Carga-total-cada-N.txt", std::ios_base::app);
        //outputFile << charge  <<"\t" << fPETime[0] <<"\n";

	for (size_t i = 0; i < fPETime.size() || i == 0; ++i) 
	{
           if(fPETime.size()==0){
	      outputFile << fPETime.size()  <<"\t" << i <<"\t" << 0 <<"\n";
	   }

	   else if (fPETime.size()!= 0){
		// Realiza alguna operación con fPETime[i]
            //std::ofstream outputFile("Carga-total-cada-N.txt", std::ios_base::app);
            outputFile << fPETime.size()  <<"\t" << i <<"\t" << fPETime[i] <<"\n";
	   }
	}



	// add total PE time distribution
	odSimData.AddPETimeDistribution(fPETime);
	// add components PE time distribution
	odSimData.AddPETimeDistribution(particleComponent, fPETimeComp);
	odSimData.AddPETimeDistribution(Particle::eMuonDecay, fPETimeMuDecay);
	odSimData.AddCharge(charge);

	fPETime.clear();
	fPETimeComp.clear();
	fPETimeMuDecay.clear();

}

G4bool
G4MPMTAction::ProcessHits(G4Step* const step, G4TouchableHistory* const /*rOHist*/)
{
	G4Track* const track = step->GetTrack();

	// The PMT solid is an effective absorbing photocathode.  Its response must
	// be sampled exactly once, when an optical photon enters the volume.
	if (track->GetDefinition() != G4OpticalPhoton::OpticalPhotonDefinition())
		return false;
	if (step->GetPreStepPoint()->GetStepStatus() != fGeomBoundary)
		return false;

	const int parentId = track->GetParentID();
	const double time = step->GetPreStepPoint()->GetGlobalTime() / CLHEP::second;
	if (time >= 1*CLHEP::second) {
		track->SetTrackStatus(fStopAndKill);
		return false;
	}

	auto& pmt = fEvent.GetDetector(fDetectorId).GetOptDevice(fOptDeviceId);
	const double energy = step->GetPreStepPoint()->GetKineticEnergy() / CLHEP::eV;
	const std::vector<double> opticalRange = pmt.GetOpticalRange();
	if (energy < opticalRange[0] || energy > opticalRange[1]) {
		track->SetTrackStatus(fStopAndKill);
		return false;
	}

	SimData& simData = fEvent.GetSimData();
	if (simData.GetSimulationMode() == SimData::SimulationMode::eFull &&
	    !pmt.IsPhotonDetected(energy)) {
		track->SetTrackStatus(fStopAndKill);
		return false;
	}

	DetectorSimData& detSimData = simData.GetDetectorSimData(fDetectorId);
	const auto& muDecayIDs = detSimData.GetMuonDecayID();
	if (muDecayIDs.find(parentId) != muDecayIDs.end()) {
		fPETimeMuDecay.push_back(time);
		++NumPEMuDecay;
	}

	fPETime.push_back(time);
	fPETimeComp.push_back(time);
	++NumPE;

	// Detection is terminal in this effective model.  This prevents the same
	// photon from generating multiple photoelectrons in later Pyrex steps.
	track->SetTrackStatus(fStopAndKill);
	return true;

}
	
