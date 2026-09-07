#include <iostream>
#include <cmath>

#include "SaltyWCD.h"
#include "Geometry.h"
#include "G4MDetectorAction.h"
#include "G4MPMTAction.h"

#include "G4VisAttributes.hh"
#include "G4NistManager.hh"
#include "G4Colour.hh"
#include "G4Tubs.hh"
#include "G4Ellipsoid.hh"
#include "G4PVPlacement.hh"
#include "G4LogicalVolume.hh"
#include "G4LogicalBorderSurface.hh"
#include "G4SDManager.hh"
#include "G4SystemOfUnits.hh"

using namespace std;

namespace
{
    // This helper is only for selecting one of the materials already built in
    // Materials.cc.  It does NOT create a new chemical material here.
    G4double NormalizeDetectorNaClInput(G4double x)
    {
        // Accept 0.025 and 2.5 as the same input convention.
        if (x > 1.0) x /= 100.0;

        if (x < 0.0)  x = 0.0;
        if (x > 0.30) x = 0.30;

        return x;
    }

    G4Material* SelectWCDMedium(Materials& mat, G4double userNaClValue)
    {
        const G4double p = NormalizeDetectorNaClInput(userNaClValue);
        const G4double tol = 1.0e-6;

        if (p <= 1.0e-12) {
            return mat.Water;
        }

        // Convention used in Materials.cc:
        // p = m_NaCl / m_H2O
        if (std::abs(p - 0.025) < tol) {
            return mat.SaltyWater_2p5;
        }
        if (std::abs(p - 0.05) < tol) {
            return mat.SaltyWater_5;
        }
        if (std::abs(p - 0.10) < tol) {
            return mat.SaltyWater_10;
        }

        // SaltyWCD.cc should not build chemistry.  If a non-tabulated
        // concentration is requested, choose the nearest predefined material.
        if (p < 0.0375) {
            G4cout << "[WARNING] SaltyWCD: NaCl fraction " << p
                   << " is not predefined. Using SaltyWater_2p5." << G4endl;
            return mat.SaltyWater_2p5;
        }
        if (p < 0.075) {
            G4cout << "[WARNING] SaltyWCD: NaCl fraction " << p
                   << " is not predefined. Using SaltyWater_5." << G4endl;
            return mat.SaltyWater_5;
        }

        G4cout << "[WARNING] SaltyWCD: NaCl fraction " << p
               << " is not predefined. Using SaltyWater_10." << G4endl;
        return mat.SaltyWater_10;
    }
}

void
SaltyWCD::BuildDetector(G4LogicalVolume* logMother,
                        Detector& detector,
                        Event& theEvent,
                        G4bool fCheckOVerlaps)
{
    // --------------------------------------------------------------------
    // Materials
    // --------------------------------------------------------------------
    Materials mat;

    G4NistManager* nist = G4NistManager::Instance();
    G4Material* StainlessSteel =
        nist->FindOrBuildMaterial("G4_STAINLESS-STEEL");

    const G4double fNaClFracMass = detector.GetImpuritiesFraction();
    G4Material* DetectorMedium = SelectWCDMedium(mat, fNaClFracMass);

    // --------------------------------------------------------------------
    // WCD dimensions
    // --------------------------------------------------------------------
    // In this geometry detector.GetTankRadius() and detector.GetTankHeight()
    // are interpreted as the active water/saline-water dimensions.
    //
    // Active volume:
    //   diameter = 96 cm  -> radius = 48 cm
    //   height   = 133 cm
    //
    // Layer sequence:
    //   active water/saline water -> Tyvek liner -> stainless-steel casing
    // --------------------------------------------------------------------
    const G4double fWaterRadius     = detector.GetTankRadius();
    const G4double fWaterHeight     = detector.GetTankHeight();
    const G4double fWaterHalfHeight = 0.5 * fWaterHeight;

    const G4double fSteelThickness  = detector.GetTankThickness();
    const G4double fTyvekThickness  = 0.12 * mm;

    const G4double fTyvekOuterRadius = fWaterRadius + fTyvekThickness;
    const G4double fSteelOuterRadius = fTyvekOuterRadius + fSteelThickness;

    const G4double fTyvekSideHalfHeight = fWaterHalfHeight;
    const G4double fSteelSideHalfHeight = fWaterHalfHeight + fTyvekThickness;

    // --------------------------------------------------------------------
    // PMT properties
    // --------------------------------------------------------------------
    OptDevice pmt = detector.GetOptDevice(OptDevice::ePMT);

    const G4double fPMTSemiX = pmt.GetSemiAxisX() * CLHEP::cm;
    const G4double fPMTSemiY = pmt.GetSemiAxisY() * CLHEP::cm;
    const G4double fPMTSemiZ = pmt.GetSemiAxisZ() * CLHEP::cm;

    // --------------------------------------------------------------------
    // Detector position
    // --------------------------------------------------------------------
    G4ThreeVector detectorPos = Geometry::ToG4Vector(detector.GetDetectorPosition(), 1.);

    const G4double fTankPosX = detectorPos.getX();
    const G4double fTankPosY = detectorPos.getY();
    const G4double fTankPosZ = detectorPos.getZ();

    // Bottom reference is fTankPosZ.  The active water volume starts after
    // the bottom steel plate and the bottom Tyvek sheet.
    const G4double zSteelBot  = fTankPosZ + 0.5*fSteelThickness;
    const G4double zTyvekBot  = fTankPosZ + fSteelThickness + 0.5*fTyvekThickness;
    const G4double zWater     = fTankPosZ + fSteelThickness + fTyvekThickness
                                + fWaterHalfHeight;
    const G4double zTyvekTop  = fTankPosZ + fSteelThickness + fTyvekThickness
                                + fWaterHeight + 0.5*fTyvekThickness;
    const G4double zSteelTop  = fTankPosZ + fSteelThickness + fTyvekThickness
                                + fWaterHeight + fTyvekThickness
                                + 0.5*fSteelThickness;

    const G4ThreeVector waterCenter(fTankPosX, fTankPosY, zWater);

    const int detectorId = detector.GetId();
    const int pmtId = 0;
    
    ostringstream namedetector;
    namedetector << "/SaltyWCD" << detectorId;

    G4cout << "[INFO] G4Models::SaltyWCD: Building detector "
           << namedetector.str()
           << " (ID = " << detectorId << ") with "
           << pmt.GetName() << "." << G4endl;

    G4cout << "[INFO] G4Models::SaltyWCD: Active medium = "
           << DetectorMedium->GetName() << G4endl;
    G4cout << "[INFO] G4Models::SaltyWCD: Water radius = "
           << fWaterRadius / CLHEP::cm << " cm" << G4endl;
    G4cout << "[INFO] G4Models::SaltyWCD: Water height = "
           << fWaterHeight / CLHEP::cm << " cm" << G4endl;
    G4cout << "[INFO] G4Models::SaltyWCD: Tyvek thickness = "
           << fTyvekThickness / CLHEP::mm << " mm" << G4endl;
    G4cout << "[INFO] G4Models::SaltyWCD: Steel thickness = "
           << fSteelThickness / CLHEP::mm << " mm" << G4endl;

    /****************************************************************
        Geometry model

        The WCD is built as explicit, non-overlapping layers:

        1. Active volume:
           pure water or predefined saline water material:
           Water, SaltyWater_2p5, SaltyWater_5, SaltyWater_10.

        2. Tyvek liner:
           material Materials::HDPE, named Tyvek_HDPE in Materials.cc.
           Its optical behavior is controlled by Materials::LinerOptSurf.

        3. Stainless-steel external casing:
           G4_STAINLESS-STEEL from NIST.

        4. PMT:
           ellipsoidal Pyrex window placed inside the active volume and
           registered as a sensitive detector.
    ****************************************************************/

    // --------------------------------------------------------------------
    // Solids
    // --------------------------------------------------------------------
    G4Tubs* solidWater = new G4Tubs("WaterVolume",
                                    0.0,
                                    fWaterRadius,
                                    fWaterHalfHeight,
                                    0.0,
                                    360.0*deg);

    G4Tubs* solidTyvekBot = new G4Tubs("TyvekBottom",
                                       0.0,
                                       fTyvekOuterRadius,
                                       0.5*fTyvekThickness,
                                       0.0,
                                       360.0*deg);

    G4Tubs* solidTyvekTop = new G4Tubs("TyvekTop",
                                       0.0,
                                       fTyvekOuterRadius,
                                       0.5*fTyvekThickness,
                                       0.0,
                                       360.0*deg);

    G4Tubs* solidTyvekSide = new G4Tubs("TyvekSide",
                                        fWaterRadius,
                                        fTyvekOuterRadius,
                                        fTyvekSideHalfHeight,
                                        0.0,
                                        360.0*deg);

    G4Tubs* solidSteelBot = new G4Tubs("SteelBottom",
                                       0.0,
                                       fSteelOuterRadius,
                                       0.5*fSteelThickness,
                                       0.0,
                                       360.0*deg);

    G4Tubs* solidSteelTop = new G4Tubs("SteelTop",
                                       0.0,
                                       fSteelOuterRadius,
                                       0.5*fSteelThickness,
                                       0.0,
                                       360.0*deg);

    G4Tubs* solidSteelSide = new G4Tubs("SteelSide",
                                        fTyvekOuterRadius,
                                        fSteelOuterRadius,
                                        fSteelSideHalfHeight,
                                        0.0,
                                        360.0*deg);

    G4Ellipsoid* solidPMT = new G4Ellipsoid("PMT",
                                            fPMTSemiX,
                                            fPMTSemiY,
                                            fPMTSemiZ,
                                            -fPMTSemiZ,
                                            0.0);

    // --------------------------------------------------------------------
    // Logical volumes
    // --------------------------------------------------------------------
    G4LogicalVolume* logTank =
        new G4LogicalVolume(solidWater, DetectorMedium, "logTank", 0, 0, 0);

    G4LogicalVolume* logTyvekBot =
        new G4LogicalVolume(solidTyvekBot, mat.HDPE, "logTyvekBot", 0, 0, 0);

    G4LogicalVolume* logTyvekTop =
        new G4LogicalVolume(solidTyvekTop, mat.HDPE, "logTyvekTop", 0, 0, 0);

    G4LogicalVolume* logTyvekSide =
        new G4LogicalVolume(solidTyvekSide, mat.HDPE, "logTyvekSide", 0, 0, 0);

    G4LogicalVolume* logCasingBot =
        new G4LogicalVolume(solidSteelBot, StainlessSteel, "logCasingBot", 0, 0, 0);

    G4LogicalVolume* logCasingTop =
        new G4LogicalVolume(solidSteelTop, StainlessSteel, "logCasingTop", 0, 0, 0);

    G4LogicalVolume* logCasingSide =
        new G4LogicalVolume(solidSteelSide, StainlessSteel, "logCasingSide", 0, 0, 0);

    // --------------------------------------------------------------------
    // Physical placements
    // --------------------------------------------------------------------
    G4PVPlacement* physTank =
        new G4PVPlacement(nullptr,
                          waterCenter,
                          logTank,
                          "physTank",
                          logMother,
                          false,
                          0,
                          fCheckOVerlaps);

    G4PVPlacement* physTyvekBot =
        new G4PVPlacement(nullptr,
                          G4ThreeVector(fTankPosX, fTankPosY, zTyvekBot),
                          logTyvekBot,
                          "physTyvekBot",
                          logMother,
                          false,
                          0,
                          fCheckOVerlaps);

    G4PVPlacement* physTyvekTop =
        new G4PVPlacement(nullptr,
                          G4ThreeVector(fTankPosX, fTankPosY, zTyvekTop),
                          logTyvekTop,
                          "physTyvekTop",
                          logMother,
                          false,
                          0,
                          fCheckOVerlaps);

    G4PVPlacement* physTyvekSide =
        new G4PVPlacement(nullptr,
                          waterCenter,
                          logTyvekSide,
                          "physTyvekSide",
                          logMother,
                          false,
                          0,
                          fCheckOVerlaps);

    new G4PVPlacement(nullptr,
                      G4ThreeVector(fTankPosX, fTankPosY, zSteelBot),
                      logCasingBot,
                      "physCasingBot",
                      logMother,
                      false,
                      0,
                      fCheckOVerlaps);

    new G4PVPlacement(nullptr,
                      G4ThreeVector(fTankPosX, fTankPosY, zSteelTop),
                      logCasingTop,
                      "physCasingTop",
                      logMother,
                      false,
                      0,
                      fCheckOVerlaps);

    new G4PVPlacement(nullptr,
                      waterCenter,
                      logCasingSide,
                      "physCasingSide",
                      logMother,
                      false,
                      0,
                      fCheckOVerlaps);

    // --------------------------------------------------------------------
    // Optical border surfaces: active medium -> Tyvek
    // --------------------------------------------------------------------
    new G4LogicalBorderSurface("WaterTyvekTopSurface",
                               physTank,
                               physTyvekTop,
                               mat.LinerOptSurf);

    new G4LogicalBorderSurface("WaterTyvekBottomSurface",
                               physTank,
                               physTyvekBot,
                               mat.LinerOptSurf);

    new G4LogicalBorderSurface("WaterTyvekSideSurface",
                               physTank,
                               physTyvekSide,
                               mat.LinerOptSurf);
                               
    // --------------------------------------------------------------------
    // PMT
    // --------------------------------------------------------------------
    string logName = "logPMT_" + to_string(pmtId);

    G4LogicalVolume* logPMT =
        new G4LogicalVolume(solidPMT, mat.Pyrex, logName, 0, 0, 0);

    // PMT centered in x,y and located at the upper part of the active volume.
    // The ellipsoid is truncated between -fPMTSemiZ and 0.
    // Therefore, its flat face is located at z = zPMT.
    // A small offset avoids numerical problems due to exact boundary contact.
    const G4double zPMT = fWaterHalfHeight - 0.1*mm;

    new G4PVPlacement(nullptr,
                      G4ThreeVector(0.0, 0.0, zPMT),
                      logPMT,
                      "physPMT",
                      logTank,
                      false,
                      pmtId,
                      fCheckOVerlaps);

    // --------------------------------------------------------------------
    // Register volumes and sensitive detectors
    // --------------------------------------------------------------------
    if (!detector.HasLogicalVolume("logTank")) {
        detector.SetLogicalVolume("logTank", logTank);
    }

    G4SDManager* const sdMan = G4SDManager::GetSDMpointer();

    if (!detector.HasOptDevice(pmtId)) {
        detector.MakeOptDevice(pmtId, OptDevice::ePMT);
        G4cout << "[DEBUG] Adding PMT id = " << pmtId << G4endl;
    }

    OptDevice optDevice = detector.GetOptDevice(pmtId);
    G4cout << "[DEBUG] Getting " << optDevice.GetName()
           << " with id " << optDevice.GetId() << G4endl;

    string optName = pmt.GetName() + "_" + to_string(pmtId);

    ostringstream fullName;
    fullName << "/SaltyWCD_/" << detectorId << "/" << optName;

    G4MPMTAction* const pmtSD =
        new G4MPMTAction(fullName.str().c_str(), detectorId, pmtId, theEvent);

    sdMan->AddNewDetector(pmtSD);
    logPMT->SetSensitiveDetector(pmtSD);

    G4MDetectorAction* const waterSD =
        new G4MDetectorAction(namedetector.str().c_str(), detectorId, theEvent);

    sdMan->AddNewDetector(waterSD);
    logTank->SetSensitiveDetector(waterSD);
}
