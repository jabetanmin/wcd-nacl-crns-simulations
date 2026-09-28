// Registro de informacion paso a paso del modelo WCD.

#ifndef G4WCDSteppingAction_h
#define G4WCDSteppingAction_h 1

#include "G4UserSteppingAction.hh"

#include "Event.h"

class G4Step;
class G4WCDConstruction;
class G4WCDEventAction;

class G4WCDSteppingAction : public G4UserSteppingAction
{
  public:
    G4WCDSteppingAction(const G4WCDConstruction* detector,
                        G4WCDEventAction* eventAction,
                        Event& event);

    ~G4WCDSteppingAction() override = default;

    void UserSteppingAction(const G4Step* step) override;

  private:
    // Se conservan estas referencias para mantener la interfaz de MEIGA y
    // permitir que la clase se amplie posteriormente sin cambiar su constructor.
    const G4WCDConstruction* fDetectorConstruction;
    G4WCDEventAction* fEventAction;
    Event& fEvent;
};

#endif
