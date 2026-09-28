// definition of the G4WCDSteppingAction class

#ifndef G4WCDSteppingAction_h
#define G4WCDSteppingAction_h 1
#include <iostream>
#include "G4UserSteppingAction.hh"
#include "G4String.hh"

#include "Event.h"


class G4WCDConstruction;
class G4WCDEventAction;

/* Stepping action class.
     UserSteppingAction collects info at a step level
*/

class G4WCDSteppingAction : public G4UserSteppingAction
{
    public:
        G4WCDSteppingAction(const G4WCDConstruction* det, G4WCDEventAction* event, Event& theEvent);
        virtual ~G4WCDSteppingAction();
        virtual void UserSteppingAction(const G4Step* step);

    private:
        const G4WCDConstruction* fDetectorConstruction;
        G4WCDEventAction* fEventAction;
        std::ofstream* fOutputFile;
        Event& fEvent;
        
        G4int eventCounter; // Contador de eventos
        G4int previousEventID; // Almacena el ID del evento anterior


        G4double fSiPMTime;
        G4double fScinTime;
        G4String stepVolume;
        G4String trackVolume;

	std::map<G4String, G4int> fReactionsPerEvent; // Mapa para registrar las reacciones
};

#endif
