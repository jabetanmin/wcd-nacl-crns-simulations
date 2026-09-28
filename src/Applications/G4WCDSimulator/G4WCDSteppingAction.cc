// implementation of the G4WCDSteppingAction class
#include "G4WCDSimulator.h"
#include "G4WCDSteppingAction.h"
#include "G4WCDConstruction.h"
#include "G4WCDEventAction.h"
#include "G4WCDTrackingAction.h"

#include "G4Step.hh"
#include "G4Track.hh"
#include "G4RunManager.hh"

#include "G4OpticalPhoton.hh"

#include "SimData.h"
#include "Detector.h"

G4WCDSteppingAction::G4WCDSteppingAction(const G4WCDConstruction* det, G4WCDEventAction* G4event, Event& theEvent)
	: G4UserSteppingAction(),
		fDetectorConstruction(det),
		fEventAction(G4event),
    fEvent(theEvent)
{

    // Inicializa el mapa para registrar las reacciones
    fReactionsPerEvent.clear();
}

G4WCDSteppingAction::~G4WCDSteppingAction()
{
}

void
G4WCDSteppingAction::UserSteppingAction(const G4Step* step)
{
    G4double paso = step->GetTrack()->GetCurrentStepNumber();
    G4Track* track = step->GetTrack();
    G4String particleName = track->GetParticleDefinition()->GetParticleName();
    G4StepPoint* preStepPoint = step->GetPreStepPoint();
    G4ThreeVector position_i = preStepPoint->GetPosition();
    G4double x_i = position_i.x(); // Coordenada x
    G4double y_i = position_i.y(); // Coordenada y
    G4double z_i = position_i.z(); // Coordenada z
    G4double E_i = preStepPoint->GetKineticEnergy();
    G4StepPoint* postStepPoint = step->GetPostStepPoint();
    G4ThreeVector position_f = postStepPoint->GetPosition();
    G4double x_f = position_f.x(); // Coordenada x
    G4double y_f = position_f.y(); // Coordenada y
    G4double z_f = position_f.z(); // Coordenada z
    G4double E_f = postStepPoint->GetKineticEnergy();
    G4String processName = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
    G4double parentID = step->GetTrack()->GetParentID();
    G4int trackID = track->GetTrackID();
   

    std::ofstream outputFileinformacion("Datos-simulacion/informacion-completa.txt", std::ios_base::app);
    outputFileinformacion << paso <<"\t" << particleName <<"\t" << trackID <<"\t"<< parentID <<"\t"<<  E_i / MeV <<"\t"<< x_i <<"\t"<< y_i <<"\t" << z_i <<"\t" << x_f<<"\t"<<y_f<<"\t"<<z_f <<"\t"<< E_f / MeV <<"\t" << postStepPoint->GetProcessDefinedStep()->GetProcessName()<< "\n";
    outputFileinformacion.close();

    if(paso == 1 && particleName == "neutron"  )
    { std::ofstream outputFileisertados("Datos-simulacion/neutrones-incertados.txt", std::ios_base::app);
    outputFileisertados << paso <<"\t" << particleName <<"\t" << trackID <<"\t"<< parentID <<"\t"<<  E_i / MeV <<"\t"<< x_i <<"\t"<< y_i <<"\t" << z_i <<"\t" << x_f<<"\t"<<y_f<<"\t"<<z_f <<"\t"<< E_f / MeV <<"\t" << postStepPoint->GetProcessDefinedStep()->GetProcessName()<< "\n";
    outputFileisertados.close();}

    if( particleName == "neutron"  )
    { std::ofstream outputFilecompleto("Datos-simulacion/interaccion-completa-neutrones.txt", std::ios_base::app);
    outputFilecompleto << paso <<"\t" << particleName <<"\t" << trackID <<"\t"<< parentID <<"\t"<<  E_i / MeV <<"\t"<< x_i <<"\t"<< y_i <<"\t" << z_i <<"\t" << x_f<<"\t"<<y_f<<"\t"<<z_f <<"\t"<< E_f / MeV <<"\t" << postStepPoint->GetProcessDefinedStep()->GetProcessName()<< "\n";
    outputFilecompleto.close();}



   //////////////////////////////////////////Hasta aqui/////////////////////

  /*  if (fReactionsPerEvent.find(processName) == fReactionsPerEvent.end()) 
    {
        // Si el proceso no está registrado, inicializa el conteo
        fReactionsPerEvent[processName] = 1;
    } 
    else {
        // Incrementa el conteo del proceso
        fReactionsPerEvent[processName]++;
    }

    // Si es el último paso en el volumen principal, imprime las reacciones del evento
    if (step->GetTrack()->GetTrackID() == 1 && step->IsLastStepInVolume()) 
    {
        G4cout << "\n Lista de reacciones nucleares en este evento: \n" << G4endl;

        for (const auto& reaction : fReactionsPerEvent) 
	{
            G4cout << "  " << std::setw(30) << reaction.first << ": "
                   << std::setw(7) << reaction.second << G4endl;
        }
    }*/

////////////////////////////////para el inicio////////////////////





   //G4Track* track = step->GetTrack();
   //G4String particleName = track->GetDynamicParticle()->GetDefinition()->GetParticleName();
   
   
   //G4ParticleDefinition* particle = track->GetDefinition();
   //G4String motherParticleName = "None";
   G4ThreeVector position = track->GetPosition();
   G4double x = position.x();
   G4double y = position.y();
   G4double z = position.z();
   //G4double time = track->GetGlobalTime();
   G4double energy = track->GetKineticEnergy();
   //G4double parentID = step->GetTrack()->GetParentID();
   //G4double paso = step->GetTrack()->GetCurrentStepNumber();
   //G4int trackID = track->GetTrackID();
   // G4String processName = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
   

    
   //G4String processName_pos = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
   //G4String processNamepre = step->GetPreStepPoint()->GetProcessDefinedStep()->GetProcessName();
   G4double preProcessEnergy = step->GetPreStepPoint()->GetKineticEnergy();
   G4double postProcessEnergy = step->GetPostStepPoint()->GetKineticEnergy();


//if (parentID > 0) {
   //G4String  motherParticleName = track->GetDynamicParticle()->GetPrimaryParticle()->GetParticleDefinition()->GetParticleName();
  
  //  }

   std::ofstream outputFileparticles("Datos-simulacion/rastreo-completo-particulas.txt", std::ios_base::app);
   outputFileparticles << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName <<"\t"<< x << "\t" << y << "\t" << z << "\t" << preProcessEnergy <<"\t" << energy / MeV << "\t" << postProcessEnergy << "\n";
    outputFileparticles.close();

    //if (particleName == "neutron" )
      // {

        // G4double zTopCap = 66.5*cm;  // Cambia si la tapa está en otra altura
        // G4double radiusCylinder = 48.0 *cm;  // Radio del cilindro

         //if (z == zTopCap && std::sqrt(x*x + y*y) <= radiusCylinder)
          //  {

            //std::ofstream outputFileneutroncruce("Datos-simulacion/neutrons_crossing_top.txt", std::ios_base::app);
            //outputFileneutroncruce << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<<  x << "\t" << y << "\t" << z << "\t" << preProcessEnergy <<"\t" <<  energy / MeV << "\t" << postProcessEnergy << "\n";
            //} 
     // }


    // Log basic neutron data



 if (particleName == "neutron")
   {
 
     std::ofstream outputFileneutron("Datos-simulacion/rastreo-neutron-completo.txt", std::ios_base::app);
     outputFileneutron << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName << "\t" << x << "\t" << y << "\t" << z << "\t" << preProcessEnergy <<"\t" <<  energy / MeV << "\t" << postProcessEnergy << "\n";
   
     //outputFileneutron.close();


     //std::ofstream outputFile("captured_neutrons.txt", std::ios_base::app);
     //       outputFile << "Energy: " << energy / CLHEP::eV << " eV, "
      //                 << "Position: " << position.x() / CLHEP::cm << " cm, "
      //                 << position.y() / CLHEP::cm << " cm, "
      //                 << position.z() / CLHEP::cm << " cm\n";
      //      outputFile.close();



      //G4double zTopCap = 130*cm;  // Cambia si la tapa está en otra altura
      //G4double radiusCylinder = 48.0 *cm;  // Radio del cilindro

     //if (position.z() <= zTopCap && std::sqrt(position.x() * position.x() + position.y() * position.y()) <= radiusCylinder) 
       // {

        //std::ofstream outputFileneutroncruce("Datos-simulacion/neutrons_crossing_top.txt", std::ios_base::app);
        //outputFileneutroncruce << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<<  x << "\t" << y << "\t" << z << "\t" << preProcessEnergy <<"\t" <<  energy / MeV << "\t" << postProcessEnergy << "\n";
       //}

    if (processName == "nCapture" ) //&&  parentID == 0 
      {
       
       //const G4Nucleus* targetNucleus = hadronicProcess->GetTargetNucleus();
       //if (!targetNucleus) return;

       // Identificar si el núcleo objetivo es hidrógeno
       //G4int Z = targetNucleus->GetZ_asInt();  
       //G4int A = targetNucleus->GetA_asInt();  
	      
       //G4String materialName = step->GetPreStepPoint()->GetMaterial()->GetName();
       //if (materialName != "Water") return;
       //if (parentID != 1 ) return;

        G4ThreeVector captureposition = track->GetPosition();
        G4double xcn = captureposition.x();
        G4double ycn = captureposition.y();
        G4double zcn = captureposition.z();
        //G4double captureEnergy = track->GetKineticEnergy();
        G4double preCaptureEnergy = step->GetPreStepPoint()->GetKineticEnergy();
        G4double postCaptureEnergy = step->GetPostStepPoint()->GetKineticEnergy();
        //G4String processNamepos = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
        //G4String processNamepre = step->GetPreStepPoint()->GetProcessDefinedStep()->GetProcessName();
         
        
        // Identificar el elemento del núcleo objetivo
    	const G4Material* material = step->GetPreStepPoint()->GetMaterial();
    	const G4Element* elemento = material->GetElement(0); // Primer elemento del material
    	G4String elementName = elemento->GetName();
    	G4int Z = elemento->GetZ(); // Número atómico
    	// G4int A = elemento->GetN(); // Número de masa si está disponible

    	// Abrir archivos para registrar los datos
    	std::ofstream outputFileTotal("Datos-simulacion/neutrones-capturados.txt", std::ios_base::app);

    	if (Z ==  8 && elementName == "Oxygen") { // Oxigeno
        	std::ofstream outputFileCl35("Datos-simulacion/neutrones-capturados-Cl35.txt", std::ios_base::app);
        	outputFileCl35 << particleName << "\t" << trackID << "\t" << parentID << "\t" << paso << "\t"<< processName << "\t" << xcn << "\t" << ycn << "\t" << zcn << "\t"<< preCaptureEnergy << "\t" << energy / MeV << "\t" << postCaptureEnergy << "\n";
        	outputFileCl35.close();
    	} else if (Z == 1 && elementName == "Hydrogen") { // Hidrógeno
        	std::ofstream outputFileH("Datos-simulacion/neutrones-capturados-hidrogeno.txt", std::ios_base::app);
        outputFileH << particleName << "\t" << trackID << "\t" << parentID << "\t" << paso << "\t"<< processName << "\t" << xcn << "\t" << ycn << "\t" << zcn << "\t" << preCaptureEnergy << "\t" << energy / MeV << "\t" << postCaptureEnergy << "\n";
        outputFileH.close();
    }

    // Registrar en el archivo general
    outputFileTotal << particleName << "\t" << trackID << "\t" << parentID << "\t" << paso << "\t"<< processName << "\t" << xcn << "\t" << ycn << "\t" << zcn << "\t"<< preCaptureEnergy << "\t" << energy / MeV << "\t" << postCaptureEnergy << "\n";
    outputFileTotal.close();

        // std::ofstream outputFilecaneutron1("Datos-simulacion/neutrones-capturados.txt", std::ios_base::app);
        // outputFilecaneutron1 << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName << "\t" <<  xcn << "\t" << ycn << "\t" << zcn << "\t" << preCaptureEnergy <<"\t" << energy / MeV <<"\t" << postCaptureEnergy <<"\n";
         
         //outputFilecaneutron1.close();
         // Get secondary particlesof capture
         const std::vector<const G4Track*>* secondaries = step->GetSecondaryInCurrentStep();
         for (size_t i = 0; i < secondaries->size(); ++i)
           {
              const G4Track* secondary = (*secondaries)[i];
              G4String particleNamesp = secondary->GetDefinition()->GetParticleName();
              G4ThreeVector positionsp = secondary->GetPosition();
	      G4double xsp = positionsp.x();
              G4double ysp = positionsp.y();
              G4double zsp = positionsp.z();
              G4double energysp = secondary->GetKineticEnergy();
	      G4double parentIDspCn = step->GetTrack()->GetParentID();
              G4double pasospCn = step->GetTrack()->GetCurrentStepNumber();
              G4int trackIDspCn = track->GetTrackID();
              std::ofstream outputFilecaneutronsc("Datos-simulacion/secondary-particles-neutron-capturado.txt", std::ios_base::app);
              outputFilecaneutronsc << particleNamesp << "\t" << trackIDspCn <<"\t" << parentIDspCn <<"\t"<< pasospCn <<"\t"<< processName << "\t" << xsp << "\t" << ysp << "\t" << zsp << "\t" << energysp / MeV <<"\n";

             outputFilecaneutronsc.close();

	  }
         // outputFilecaneutron1.close();
        }
       
  
       if (processName == "neutronInelastic" )
          {
           G4ThreeVector ninelasticposition = track->GetPosition();
           G4double xni = ninelasticposition.x();
           G4double yni = ninelasticposition.y();
           G4double zni = ninelasticposition.z();
           G4double ninelasticEnergy = track->GetKineticEnergy();

           std::ofstream outputFilecaneutronin("Datos-simulacion/neutron-inelastico-punto.txt", std::ios_base::app);
           outputFilecaneutronin << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<<processName << "\t" << xni << "\t" << yni << "\t" << zni << "\t" << ninelasticEnergy / MeV <<"\n";

	   outputFilecaneutronin.close();
           // Get secondary particles
           const std::vector<const G4Track*>* secondariesni = step->GetSecondaryInCurrentStep();
           for (size_t j = 0; j < secondariesni->size(); ++j)
               {
                const G4Track* secondaryni = (*secondariesni)[j];
                G4String particleNamesni = secondaryni->GetDefinition()->GetParticleName();
                G4ThreeVector positionni = secondaryni->GetPosition();
                G4double xin = positionni.x();
                G4double yin = positionni.y();
                G4double zin = positionni.z();
                G4double energyni = secondaryni->GetKineticEnergy();

                std::ofstream outputFilecaneutronsin("Datos-simulacion/secondary-particles-neutron-inelastic.txt", std::ios_base::app);
                outputFilecaneutronsin << particleNamesni << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName << "\t" << xin << "\t" << yin << "\t" << zin << "\t" << energyni / MeV <<"\n";
                outputFilecaneutronsin.close();
	       }
           }
           outputFileneutron.close();
       }
//}
//////////////////////////SECCION GAMMAS////////////////////////////////////////////////////////////////////////////////////////////////

       //if (particleName == "gamma" &&  parentID == 1) {
   if (particleName == "gamma")
    {
       std::ofstream outputFilegamma1("Datos-simulacion/gamma-completo.txt", std::ios_base::app);
       outputFilegamma1 << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<<processName << "\t" << x << "\t" << y << "\t" << z << "\t" << energy / MeV <<"\n";
      outputFilegamma1.close();
	      
      if (processName == "phot" || processName == "compt" || processName == "conv" || processName=="Rayl" )
        {//|| processName=="Rayl"
          G4ThreeVector comptposition = track->GetPosition();
           G4double xcmpt = comptposition.x();
           G4double ycmpt = comptposition.y();
           G4double zcmpt = comptposition.z();
           G4double comptEnergy = track->GetKineticEnergy();
           G4double precomptEnergy = step->GetPreStepPoint()->GetKineticEnergy();
           G4double postcomptEnergy = step->GetPostStepPoint()->GetKineticEnergy();
           //G4String posprocessNamega = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
           //G4String preprocessNamega = step->GetPreStepPoint()->GetProcessDefinedStep()->GetProcessName();
	   std::ofstream outputFilegammacompt("Datos-simulacion/gamma-compt-punto.txt", std::ios_base::app);
           outputFilegammacompt << particleName << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName  << "\t" <<  xcmpt << "\t" << ycmpt << "\t" << zcmpt << "\t" << precomptEnergy <<"\t" << comptEnergy / MeV  <<"\t" <<postcomptEnergy <<"\n";
          outputFilegammacompt.close();
	   
	  // Get secondary particles
       const std::vector<const G4Track*>* secondariescompt = step->GetSecondaryInCurrentStep();
           for (size_t k = 0; k < secondariescompt->size(); ++k)
               {
                const G4Track* secondarycompt = (*secondariescompt)[k];
                G4String particleNamescompt = secondarycompt->GetDefinition()->GetParticleName();
                G4ThreeVector positioncompt = secondarycompt->GetPosition();
                G4double xpcompt =positioncompt.x();
                G4double ypcompt =positioncompt.y();
                G4double zpcompt =positioncompt.z();
                G4double energycompt = secondarycompt->GetKineticEnergy();
                G4double Energyprecompt = step->GetPreStepPoint()->GetKineticEnergy();
                G4double Energypostcompt = step->GetPostStepPoint()->GetKineticEnergy();

                std::ofstream outputFilesecparcompt("Datos-simulacion/secondary-particles-gamma-compton.txt", std::ios_base::app);
                outputFilesecparcompt << particleNamescompt << "\t" << trackID <<"\t" << parentID <<"\t"<< paso <<"\t"<< processName << "\t" << xpcompt << "\t" << ypcompt << "\t" << zpcompt << "\t" <<  Energyprecompt << "\t" <<   energycompt / MeV <<"\t" << Energypostcompt << "\n";
                outputFilesecparcompt.close();
  
	       }
         }
     }

//////////////////SECCION ELECTRONES/////////////////////////////////////////////////////////////////////////////////////////////////

      if (particleName == "e-" || particleName == "e+" )
       {
          std::ofstream outputFilelectron("Datos-simulacion/rastreo-electron.txt", std::ios_base::app);
          outputFilelectron << particleName << "\t" << processName <<"\t" << trackID <<"\t" << parentID <<"\t" << paso <<"\t"<< x << "\t" << y << "\t" << z <<"\t" <<  energy / MeV << "\n";
       
	  outputFilelectron.close();
          if (processName == "Cerenkov" )
             {
              G4ThreeVector cerenkovposition = track->GetPosition();
              G4double xck = cerenkovposition.x();
              G4double yck = cerenkovposition.y();
              G4double zck = cerenkovposition.z();
              //G4double captureEnergy = track->GetKineticEnergy();
              //G4double preCerenkovEnergy = step->GetPreStepPoint()->GetKineticEnergy();
              //G4double postCerenkovEnergy = step->GetPostStepPoint()->GetKineticEnergy();
              //G4String processNamepos = step->GetPostStepPoint()->GetProcessDefinedStep()->GetProcessName();
              //G4String processNamepre = step->GetPreStepPoint()->GetProcessDefinedStep()->GetProcessName();
              
	      
	    std::ofstream outputFileCerenkov("Datos-simulacion/radiacion-Cerenkov-electron.txt", std::ios_base::app);
            outputFileCerenkov << particleName << "\t" << processName <<"\t" << trackID <<"\t" << parentID <<"\t" << paso <<"\t"<< xck << "\t" << yck << "\t" << zck << "\t" <<  energy / MeV << "\n";
             outputFileCerenkov.close();
            }
       }
       //outputFilecaneutronsc.close();
       //outputFilecaneutron1.close();  
       //outputFilecaneutronin.close();
       //outputFilecaneutronsin.close();
       //outputFilegamma1.close();
       //outputFilegammacompt.close();
       //outputFilesecparcompt.close();
       //outputFilelectron.close();
       //outputFileCerenkov.close();



             fReactionsPerEvent.clear();

}
