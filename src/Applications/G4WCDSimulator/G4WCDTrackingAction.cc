#include "G4WCDTrackingAction.h"
#include "G4WCDSimulator.h"

#include <G4Track.hh>
#include <G4TrackingManager.hh>
#include <G4TrackStatus.hh>

#include "Particle.h"


void
G4WCDTrackingAction::PreUserTrackingAction(const G4Track* track)
{ 
 //override {
        G4cout << "Inicio del rastreo: "
               << "Particula: " << track->GetParticleDefinition()->GetParticleName()
               << ", Energia: " << track->GetKineticEnergy() / MeV << " MeV"
               << ", Position inicial: " << track->GetPosition() << G4endl;
   //     }
}


void
G4WCDTrackingAction::PostUserTrackingAction(const G4Track* track)
{
  //override {
        G4cout << "Punto final rastreo: "
               << "Particula: " << track->GetParticleDefinition()->GetParticleName()
               << ", Position final: " << track->GetPosition() << G4endl;
    //}
}

// Register the tracking action
//G4UserTrackingAction* trackingAction = new G4WCDTrackingAction();
//runManager->SetUserAction(trackingAaction);
