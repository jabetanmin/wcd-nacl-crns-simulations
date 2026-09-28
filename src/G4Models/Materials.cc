#include "Materials.h"
#include "G4NistManager.hh"
#include "G4Exception.hh"
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cmath>
// material properties (scintillation, Cherenkov, optics)

// array of photon energies in the red-UV range for scintillation processes
static G4double scinPhotonEnergy[] = {
	2.00*eV, 2.03*eV, 2.06*eV, 2.09*eV, 2.12*eV,
	2.15*eV, 2.18*eV, 2.21*eV, 2.24*eV, 2.27*eV,
	2.30*eV, 2.33*eV, 2.36*eV, 2.39*eV, 2.42*eV,
	2.45*eV, 2.48*eV, 2.51*eV, 2.54*eV, 2.57*eV,
	2.60*eV, 2.63*eV, 2.66*eV, 2.69*eV, 2.72*eV,
	2.75*eV, 2.78*eV, 2.81*eV, 2.84*eV, 2.87*eV,
	2.90*eV, 2.93*eV, 2.96*eV, 2.99*eV, 3.02*eV,
	3.05*eV, 3.08*eV, 3.11*eV, 3.14*eV, 3.17*eV,
	3.20*eV, 3.23*eV, 3.26*eV, 3.29*eV, 3.32*eV,
	3.35*eV, 3.38*eV, 3.41*eV, 3.44*eV, 3.47*eV
};

G4int scinArrEntries = sizeof(scinPhotonEnergy)/sizeof(G4double);

static G4double scinRefIndex[] = {
	1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
	1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
	1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
	1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5,
	1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5
};

static G4double scinAbsLen[] = {
	4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 
	4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 
	4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 4.0*cm, 
	24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 
	24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 24.0*cm, 
	24.0*cm, 24.0*cm
 };

static G4double scinFastComp[] = {
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
};

static G4double scinSlowComp[] = {
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
};

static G4double scinOptSurfRefIndex[] = {
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
	1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0
 };

static G4double scinOptSurfEff[] = {
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
	0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
 };

static G4double pmmaRefIndex[] = {
	1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60,
	1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60,
	1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60,
	1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60,
	1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60, 1.60
};

static G4double pmmaAbsLen[] = {
	10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m,
	10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m,
	10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 10.00*m, 1.0*m,
	0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m,
	0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m, 0.0001*m
};

static G4double pmmaEmission[] = {
	0.05, 0.10, 0.30, 0.50, 0.75, 1.00, 1.50, 1.85, 2.30, 2.75,
	3.25, 3.80, 4.50, 5.20, 6.00, 7.00, 8.50, 9.50, 11.1, 12.4,
	12.9, 13.0, 12.8, 12.3, 11.1, 11.0, 12.0, 11.0, 17.0, 16.9,
	15.0, 9.00, 2.50, 1.00, 0.05, 0.00, 0.00, 0.00, 0.00, 0.00,
	0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00
};


static G4double pethyRefIndex[] = {
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49, 1.49
};

static G4double pethyAbsLen[] = {
	20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m,
	20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m,
	20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m,
	20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m,
	20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m, 20.0*m
};

static G4double fpethyRefIndex[] = {
	1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42,
	1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42,
	1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42,
	1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42,
	1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42, 1.42
};

// Effective PMT absorber: cover the same 300--650 nm response range used by
// OptDevice::GetQuantumEfficiency.  RINDEX controls the Fresnel probability at
// the active-medium/PMT boundary; the very short ABSLENGTH makes transmission
// into the solid terminal.  QE is applied once in G4MPMTAction, not here.
static G4double pmtPhotonEnergy[] = {(1240.0/650.0)*eV, (1240.0/300.0)*eV};
static G4double pmtRefIndex[] = {1.47, 1.47};
static G4double pmtAbsLength[] = {0.0005*mm, 0.0005*mm};
G4int pmtArrEntries = sizeof(pmtPhotonEnergy) / sizeof(G4double);

// ------------------- Water 1 (Pierre Auger Offline Framework) -------------------------------

// array of photon energies for Cerenkov processes in WCD tanks
// this energy range corresponds to the efficiency region of Auger WCD large PMTs
static G4double water1PhotonEnergy[] = {
	2.08*eV,  2.16*eV,  2.19*eV,  2.23*eV,  2.27*eV,  2.32*eV,
	2.36*eV,  2.41*eV,  2.46*eV,  2.50*eV,  2.56*eV,  2.61*eV,
	2.67*eV,  2.72*eV,  2.79*eV,  2.85*eV,  2.92*eV,  2.99*eV,
	3.06*eV,  3.14*eV,  3.22*eV,  3.31*eV,  3.40*eV,  3.49*eV,
	3.59*eV,  3.70*eV,  3.81*eV,  3.94*eV,  4.07*eV,  4.20*eV
};

G4int water1ArrEntries = sizeof(water1PhotonEnergy) / sizeof(G4double);
G4double scaleAbsLen = 100*m;

static G4double water1AbsLen[] = {
	0.092*scaleAbsLen, 0.133*scaleAbsLen, 0.180*scaleAbsLen, 0.203*scaleAbsLen, 0.226*scaleAbsLen, 0.258*scaleAbsLen,
	0.284*scaleAbsLen, 0.302*scaleAbsLen, 0.403*scaleAbsLen, 0.560*scaleAbsLen, 0.735*scaleAbsLen, 0.818*scaleAbsLen,
	0.923*scaleAbsLen, 0.923*scaleAbsLen, 0.993*scaleAbsLen, 0.993*scaleAbsLen, 1.000*scaleAbsLen, 0.941*scaleAbsLen,
	0.889*scaleAbsLen, 0.842*scaleAbsLen, 0.754*scaleAbsLen, 0.655*scaleAbsLen, 0.480*scaleAbsLen, 0.380*scaleAbsLen,
	0.311*scaleAbsLen, 0.257*scaleAbsLen, 0.212*scaleAbsLen, 0.171*scaleAbsLen, 0.137*scaleAbsLen, 0.102*scaleAbsLen
};


static G4double water1PhotonEnergyShort[] = {2.08*eV, 4.20*eV};
static G4double water1RefIndex[] = {1.33, 1.33};


// ---------------------- Water 2 (Geant4 OpNovice example) ----------------------

// arrays from Geant4 OpNovice example
static G4double water2PhotonEnergy[] = {
		2.034 * eV, 2.068 * eV, 2.103 * eV, 2.139 * eV, 2.177 * eV, 2.216 * eV,
		2.256 * eV, 2.298 * eV, 2.341 * eV, 2.386 * eV, 2.433 * eV, 2.481 * eV,
		2.532 * eV, 2.585 * eV, 2.640 * eV, 2.697 * eV, 2.757 * eV, 2.820 * eV,
		2.885 * eV, 2.954 * eV, 3.026 * eV, 3.102 * eV, 3.181 * eV, 3.265 * eV,
		3.353 * eV, 3.446 * eV, 3.545 * eV, 3.649 * eV, 3.760 * eV, 3.877 * eV,
		4.002 * eV, 4.136 * eV
	};

// WCD refractive-index spectra on the same 32-point energy grid above.
// Arrays are intentionally non-const for compatibility with the
// G4MaterialPropertiesTable::AddProperty API in Geant4 10.07.p04.
static G4double pureWaterRefIndex[] = {
    1.3319872, 1.3324872, 1.3329872, 1.3334872, 1.3339872, 1.3344872,
    1.3349872, 1.3354872, 1.3359872, 1.3364872, 1.3369872, 1.3376872,
    1.3384872, 1.3389872, 1.3394872, 1.3402872, 1.3406872, 1.3414872,
    1.3419872, 1.3424872, 1.3429872, 1.3434872, 1.3439872, 1.3444872,
    1.3452872, 1.3456872, 1.3464872, 1.3469872, 1.3474872, 1.3479872,
    1.3484872, 1.3492872
};

static G4double saltyWater2p5RefIndex[] = {
    1.3389748, 1.3393319, 1.3396866, 1.3400397, 1.3403883, 1.3407376,
    1.3410888, 1.3414396, 1.3417951, 1.3421537, 1.3425175, 1.3430903,
    1.3437697, 1.3441624, 1.3445696, 1.3452923, 1.3456353, 1.3463984,
    1.3468882, 1.3474063, 1.3479562, 1.3485422, 1.3491666, 1.3498363,
    1.3508518, 1.3515223, 1.3526517, 1.3535431, 1.3545063, 1.3555405,
    1.3566576, 1.3581655
};

static G4double saltyWater5RefIndex[] = {
    1.3428145, 1.3431976, 1.3435767, 1.3439527, 1.3443232, 1.3446927,
    1.3450624, 1.3454307, 1.3458022, 1.3461759, 1.3465541, 1.3471392,
    1.3478302, 1.3482365, 1.3486578, 1.3493938, 1.3497542, 1.3505348,
    1.3510465, 1.3515907, 1.3521714, 1.3527942, 1.3534617, 1.3541829,
    1.3552573, 1.3559996, 1.3572114, 1.3581999, 1.3592765, 1.3604404,
    1.3617071, 1.3633853
};

static G4double saltyWater10RefIndex[] = {
    1.3588310, 1.3590937, 1.3593505, 1.3596026, 1.3598447, 1.3600849,
    1.3603250, 1.3605609, 1.3608010, 1.3610423, 1.3612880, 1.3617427,
    1.3623022, 1.3625837, 1.3628854, 1.3635060, 1.3637615, 1.3644425,
    1.3648698, 1.3653417, 1.3658659, 1.3664496, 1.3670986, 1.3678241,
    1.3689258, 1.3697281, 1.3710292, 1.3721451, 1.3733899, 1.3747644,
    1.3762907, 1.3782804
};

// Common absorption-length spectrum. In the absence of concentration-specific
// measurements, the same baseline is used for all four WCD media.
static G4double waterAbsLen[] = {
     3.448*m,  4.082*m,  6.329*m,  9.174*m,
    12.346*m, 13.889*m, 15.152*m, 17.241*m,
    18.868*m, 20.000*m, 26.316*m, 35.714*m,
    45.455*m, 47.619*m, 52.632*m, 52.632*m,
    55.556*m, 52.632*m, 52.632*m, 47.619*m,
    45.455*m, 41.667*m, 37.037*m, 33.333*m,
    30.000*m, 28.500*m, 27.000*m, 24.500*m,
    22.000*m, 19.500*m, 17.500*m, 14.500*m
};


static G4double water2PhotonEnergyMie[] = {
		1.56962 * eV, 1.58974 * eV, 1.61039 * eV, 1.63157 * eV, 1.65333 * eV,
		1.67567 * eV, 1.69863 * eV, 1.72222 * eV, 1.74647 * eV, 1.77142 * eV,
		1.7971 * eV,  1.82352 * eV, 1.85074 * eV, 1.87878 * eV, 1.90769 * eV,
		1.93749 * eV, 1.96825 * eV, 1.99999 * eV, 2.03278 * eV, 2.06666 * eV,
		2.10169 * eV, 2.13793 * eV, 2.17543 * eV, 2.21428 * eV, 2.25454 * eV,
		2.29629 * eV, 2.33962 * eV, 2.38461 * eV, 2.43137 * eV, 2.47999 * eV,
		2.53061 * eV, 2.58333 * eV, 2.63829 * eV, 2.69565 * eV, 2.75555 * eV,
		2.81817 * eV, 2.88371 * eV, 2.95237 * eV, 3.02438 * eV, 3.09999 * eV,
		3.17948 * eV, 3.26315 * eV, 3.35134 * eV, 3.44444 * eV, 3.54285 * eV,
		3.64705 * eV, 3.75757 * eV, 3.87499 * eV, 3.99999 * eV, 4.13332 * eV,
		4.27585 * eV, 4.42856 * eV, 4.59258 * eV, 4.76922 * eV, 4.95999 * eV,
		5.16665 * eV, 5.39129 * eV, 5.63635 * eV, 5.90475 * eV, 6.19998 * eV
	};

// Rayleigh scattering length calculated by G4OpRayleigh

// assumes 100 times larger than Rayleigh scattering length
static G4double water2Mie[] = {
		167024.4 * m, 158726.7 * m, 150742 * m,   143062.5 * m, 135680.2 * m,
		128587.4 * m, 121776.3 * m, 115239.5 * m, 108969.5 * m, 102958.8 * m,
		97200.35 * m, 91686.86 * m, 86411.33 * m, 81366.79 * m, 76546.42 * m,
		71943.46 * m, 67551.29 * m, 63363.36 * m, 59373.25 * m, 55574.61 * m,
		51961.24 * m, 48527.00 * m, 45265.87 * m, 42171.94 * m, 39239.39 * m,
		36462.50 * m, 33835.68 * m, 31353.41 * m, 29010.30 * m, 26801.03 * m,
		24720.42 * m, 22763.36 * m, 20924.88 * m, 19200.07 * m, 17584.16 * m,
		16072.45 * m, 14660.38 * m, 13343.46 * m, 12117.33 * m, 10977.70 * m,
		9920.416 * m, 8941.407 * m, 8036.711 * m, 7202.470 * m, 6434.927 * m,
		5730.429 * m, 5085.425 * m, 4496.467 * m, 3960.210 * m, 3473.413 * m,
		3032.937 * m, 2635.746 * m, 2278.907 * m, 1959.588 * m, 1675.064 * m,
		1422.710 * m, 1200.004 * m, 1004.528 * m, 833.9666 * m, 686.1063 * m
	};

G4int water2ArrEntries = sizeof(water2PhotonEnergy) / sizeof(G4double);

// gforward, gbackward, forward backward ratio
static G4double water2MieConst[3] = { 0.99, 0.99, 0.8 };

static G4MaterialPropertiesTable* CreateWCDOpticalTable(
    G4double* refractiveIndex)
{
    G4MaterialPropertiesTable* table = new G4MaterialPropertiesTable();
    table->AddProperty("RINDEX",
                       water2PhotonEnergy,
                       refractiveIndex,
                       water2ArrEntries);
    table->AddProperty("ABSLENGTH",
                       water2PhotonEnergy,
                       waterAbsLen,
                       water2ArrEntries);

    // Retain the pre-existing Geant4 OpNovice Mie model as a common baseline.
    // It is not a measured salinity-dependent scattering model.
    table->AddProperty("MIEHG",
                       water2PhotonEnergyMie,
                       water2Mie,
                       sizeof(water2PhotonEnergyMie)/sizeof(G4double));
    table->AddConstProperty("MIEHG_FORWARD", water2MieConst[0]);
    table->AddConstProperty("MIEHG_BACKWARD", water2MieConst[1]);
    table->AddConstProperty("MIEHG_FORWARD_RATIO", water2MieConst[2]);
    return table;
}



// ----------- Liner (Tyvek) --------------------------

static G4double linerAbsLen[] = {
	0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,
	0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,
	0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,
	0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,
	0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm,  0.1*mm
};

static G4double linerRefIndex[] = {
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49,
	1.49, 1.49, 1.49, 1.49, 1.49, 1.49
};

static G4double linerBackScatter[] = {
	0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
	0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
	0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
	0.02, 0.02, 0.02, 0.02, 0.02, 0.02,
	0.02, 0.02, 0.02, 0.02, 0.02, 0.02
};

static G4double scaleLinerRef = 0.94;
static G4double linerReflectivity[] = {
	0.9957*scaleLinerRef, 0.9953*scaleLinerRef, 0.9948*scaleLinerRef, 0.9942*scaleLinerRef, 0.9939*scaleLinerRef, 0.9937*scaleLinerRef,
	0.9937*scaleLinerRef, 0.9940*scaleLinerRef, 0.9945*scaleLinerRef, 0.9954*scaleLinerRef, 0.9964*scaleLinerRef, 0.9975*scaleLinerRef,
	0.9985*scaleLinerRef, 0.9993*scaleLinerRef, 1.0000*scaleLinerRef, 1.0000*scaleLinerRef, 0.9993*scaleLinerRef, 0.9977*scaleLinerRef,
	0.9948*scaleLinerRef, 0.9903*scaleLinerRef, 0.9840*scaleLinerRef, 0.9753*scaleLinerRef, 0.9642*scaleLinerRef, 0.9500*scaleLinerRef, 
	0.9334*scaleLinerRef, 0.9108*scaleLinerRef, 0.8849*scaleLinerRef, 0.8541*scaleLinerRef, 0.8178*scaleLinerRef, 0.7755*scaleLinerRef
};

// sigmaAlpha is used to model specular reflections from the surface
static G4double fSigmaAlpha = 0.17; // 0.23 in doi = 10.1364/OE.19.004199
static G4double specularLobePhotonEnergy[] = {2.08*eV, 3.0*eV, 4.20*eV};
// fraction of light reflected in a lobe with width characterized by sigmaAlpha
static G4double specularLobe[] = {0.02, 0.02, 0.02}; // same value in doi = 10.1364/OE.19.004199
static G4double specularSpike[] = {0, 0, 0};

// --------------------------------------------------------------------
// Utilities for saline water at 20 C
// --------------------------------------------------------------------
static G4double NormalizeNaClFraction(G4double x)
{
	// r_NaCl = m_NaCl / (m_H2O + m_NaCl).
	// Accept both 0.025 and 2.5 as input representations of 2.5% w/w.
	if (x > 1.0) x /= 100.0;
	return x;
}

static G4double WCDMediumDensity20C(G4double wNaCl)
{
	// Tabulated densities used by this study at 20 degC.
	// No interpolation is performed: only the four simulated media are valid.
	const G4double tol = 1.0e-9;
	if (std::abs(wNaCl - 0.000) < tol) return 0.99820 * g/cm3;
	if (std::abs(wNaCl - 0.025) < tol) return 1.01604 * g/cm3;
	if (std::abs(wNaCl - 0.050) < tol) return 1.03401 * g/cm3;
	if (std::abs(wNaCl - 0.100) < tol) return 1.07051 * g/cm3;

	G4ExceptionDescription description;
	description << "Unsupported NaCl final mass fraction: " << wNaCl
	            << ". Valid values are 0, 0.025, 0.050 and 0.100.";
	G4Exception("WCDMediumDensity20C", "WCD-MAT-001",
	            FatalException, description);
	return 0.0;
}

static G4String SaltyWaterName(G4double wNaCl)
{
	const G4double w = NormalizeNaClFraction(wNaCl);
	std::ostringstream os;
	os << "SaltyWater_NaCl_"
	   << std::fixed << std::setprecision(1)
	   << 100.0*w << "pct";
	return os.str();
}

static G4Material* CreateSaltyWaterByFinalMassFraction(
	const G4String& name,
	G4double wNaClInput,
	G4Element* elBoundH,
	G4Element* elO,
	G4Element* elNa,
	G4Element* elCl,
	G4MaterialPropertiesTable* opticalMPT
)
{
	// Final solution mass fraction:
	// w_NaCl = m_NaCl / (m_H2O + m_NaCl).
	const G4double wNaCl = NormalizeNaClFraction(wNaClInput);

	const G4double MH  = 1.00794;
	const G4double MO  = 15.9994;
	const G4double MNa = 22.98977;
	const G4double MCl = 35.453;

	const G4double MH2O  = 2.0*MH + MO;
	const G4double MNaCl = MNa + MCl;

	const G4double wWater = 1.0 - wNaCl;

	const G4double wH  = wWater * (2.0*MH/MH2O);
	const G4double wO  = wWater * (MO/MH2O);
	const G4double wNa = wNaCl  * (MNa/MNaCl);
	const G4double wCl = wNaCl  * (MCl/MNaCl);

	const G4double density = WCDMediumDensity20C(wNaCl);

	// Same thermal state as Water_TS_H_of_Water, and the same bound-hydrogen
	// element, so that every WCD saline medium also receives the h_water
	// S(alpha,beta) treatment below 4 eV (see G4MPhysicsList::G4MPhysicsList).
	// Na, Cl and O keep the standard G4NDL free-gas treatment: G4NDL 4.6 has
	// no concentration-specific thermal scattering law for these solutions.
	G4Material* saltyWater = new G4Material(name, density, 4,
	                                        kStateLiquid,
	                                        293.15 * kelvin,
	                                        1.0 * bar);
	saltyWater->AddElement(elBoundH, wH);
	saltyWater->AddElement(elO,  wO);
	saltyWater->AddElement(elNa, wNa);
	saltyWater->AddElement(elCl, wCl);

	// Each saline medium receives its own concentration-dependent optical
	// table (see CreateWCDOpticalTable / pureWaterRefIndex / saltyWaterNRefIndex).
	if (opticalMPT) saltyWater->SetMaterialPropertiesTable(opticalMPT);

	return saltyWater;
}


//////
static bool isInitialized = 0;
G4Element* Materials::elN;
G4Element* Materials::elO;
G4Element* Materials::elH;
G4Element* Materials::elTSHWater;
G4Element* Materials::elC;
G4Element* Materials::elSi;
G4Element* Materials::elTi;
G4Element* Materials::elB;
G4Element* Materials::elNa;
G4Element* Materials::elCa;
G4Element* Materials::elFe;
G4Element* Materials::elAl;
G4Element* Materials::elPb;
G4Element* Materials::elCl;

G4Material* Materials::SiO2;
G4Material* Materials::TiO2;
G4Material* Materials::B2O2;
G4Material* Materials::Na2O;
G4Material* Materials::PPO;
G4Material* Materials::POPOP;
G4Material* Materials::Polystyrene;

// Materials
G4Material* Materials::Air;
G4Material* Materials::Water;
G4Material* Materials::Salt;
G4Material* Materials::SaltyWater;
G4Material* Materials::SaltyWater_2p5;
G4Material* Materials::SaltyWater_5;
G4Material* Materials::SaltyWater_10;
G4Material* Materials::StdRock;
G4Material* Materials::ScinPlastic;
G4Material* Materials::ScinCoating;
G4Material* Materials::PMMA;
G4Material* Materials::Pethylene;
G4Material* Materials::FPethylene;
G4Material* Materials::Pyrex;
G4Material* Materials::HDPE;
G4Material* Materials::Concrete;
G4Material* Materials::Lead;
G4OpticalSurface* Materials::ScinOptSurf;
G4OpticalSurface* Materials::LinerOptSurf;
G4OpticalSurface* Materials::LinerOptSurf2;

G4MaterialPropertiesTable* Materials::waterPT1;
G4MaterialPropertiesTable* Materials::waterPT2;
G4MaterialPropertiesTable* Materials::linerPT1;
G4MaterialPropertiesTable* Materials::scinPT;
G4MaterialPropertiesTable* Materials::scinOptSurfPT;
G4MaterialPropertiesTable* Materials::pmmaPT;
G4MaterialPropertiesTable* Materials::pethylenePT;
G4MaterialPropertiesTable* Materials::fpethylenePT;
G4MaterialPropertiesTable* Materials::pyrexPT;
G4MaterialPropertiesTable* Materials::linerOpticalPT;

double fracMassNaCl;

Materials::Materials() 
{

	if (isInitialized) {
		return;
	}

	isInitialized = true;
	
	CreateElements();
	CreateCompounds();
	CreateMaterials();

}

Materials::~Materials()
{

}

const G4double* 
Materials::GetScinPhotonEnergyArray() const { return scinPhotonEnergy; }

const G4double*
Materials::GetScinRefIndexArray() const { return scinRefIndex; }

void
Materials::CreateElements() 
{
	
	elN  = new G4Element("Nitrogen", "N", 7, 14.01 * g/mole);
	elO  = new G4Element("Oxygen", "O", 8, 16.00 * g/mole);
	elH  = new G4Element("Hydrogen", "H", 1, 1.01 * g/mole);
	// Exact Geant4 thermal-scattering name.  G4NeutronHP maps this
	// pseudo-element to the h_water S(alpha,beta) evaluation in G4NDL.
	// Used for every WCD active medium (pure water and the three NaCl
	// solutions) so hydrogen is consistently treated as bound, not free-gas.
	elTSHWater = new G4Element("TS_H_of_Water", "H_WATER",
	                            1.0, 1.00794 * g/mole);
	elC  = new G4Element("Carbon", "C", 6, 12.0107 * g/mole);
	elSi = new G4Element("Silicon", "Si", 14, 28.09 * g/mole);
	elTi = new G4Element("Titanium", "Ti", 22, 47.867 * g/mole);
	elB  = new G4Element("Boron", "B", 5, 10.811 * g/mole);
	elNa = new G4Element("Sodium", "Na", 11, 22.98977 * g/mole);
	elCa = new G4Element("Calcium", "Ca", 20, 40.08 * g/mole);
	elFe = new G4Element("Iron", "Fe", 26, 55.850 * g/mole);
	elAl = new G4Element("Aluminium", "Al", 13, 26.98 * g/mole);
	elPb = new G4Element("Lead", "Pb", 82, 207.2 * g/mole);
	//elCl = new G4Element("Chlorine", "Cl", 17, 70.906 * g/mole);
        elCl = new G4Element("Chlorine", "Cl", 17, 35.453 * g/mole);                     
}

void
Materials::CreateCompounds()
{
	// silicon dioxide for "quartz"
	SiO2 = new G4Material("SiO2", 2.65 * g/cm3, 2);
	SiO2->AddElement(elSi, 1);
	SiO2->AddElement(elO, 2);
	// titanium dioxide
	TiO2 = new G4Material("TiO2", 4.26 * g/cm3, 2);
	TiO2->AddElement(elTi, 1);
	TiO2->AddElement(elO, 2);
	// diboron dioxide
	B2O2 = new G4Material("B2O2", 2.23 * g/cm3, 2);
	B2O2->AddElement(elB, 2);
	B2O2->AddElement(elO, 2);
	// sodium oxide
	Na2O = new G4Material("Na2O", 2.23 * g/cm3, 2);
	Na2O->AddElement(elNa, 2);
	Na2O->AddElement(elO, 1);

	// Polystyrene for the scintillator bars Dow STYRON 663 W
	Polystyrene = new G4Material("Polystrene", 1.04 * g/cm3, 2);
	Polystyrene->AddElement(elC, 8);
	Polystyrene->AddElement(elH, 8);

	// dopant materials for scintillator bars
	/* Scintillator made of Polystyrene ( C6H5-CH-CH2 ) + PPO + POPOP
			Plastic:
			Is a replication on an aromatic ring (C6H5) with one out of the six H
			replaced by a CH bond with another CH2.
								CH2
								//
								CH
								|
							 / \
			 C6H5:  |   |
							 \ /
	*/

	// PPO:
	PPO = new G4Material("PPO", 1.060 * g/cm3, 4);
	PPO->AddElement(elC, 15);
	PPO->AddElement(elH, 11);
	PPO->AddElement(elN, 1);
	PPO->AddElement(elO, 1);
	// POPOP:
	POPOP = new G4Material("POPOP", 1.060 * g/cm3, 4);
	POPOP->AddElement(elC, 24);
	POPOP->AddElement(elH, 16);
	POPOP->AddElement(elN, 2);
	POPOP->AddElement(elO, 2);
	
	// H2O:


	// Salt
	Salt = new G4Material("Salt", 2.165 * g/cm3, 2);
	Salt->AddElement(elCl, 1);
	Salt->AddElement(elNa, 1);

	//G4NistManager* nist = G4NistManager::Instance();
        //Salt = G4NistManager::Instance()->FindOrBuildMaterial("G4_SODIUM_CHLORIDE");
	//G4Material* Salt = nist->FindOrBuildMaterial("G4_SODIUM_CHLORIDE");



}

void
Materials::CreateMaterials()
{
        //Salt = G4NistManager::Instance()->FindOrBuildMaterial("G4_SODIUM_CHLORIDE");


	// --------------------------------------------------------------------
	// Air
	// --------------------------------------------------------------------
	Air = new G4Material("Air", 1.29e-3 * g/cm3, 2);
	Air->AddElement(elN, 0.7);
	Air->AddElement(elO, 0.3);
	// --------------------------------------------------------------------
	// Water
	// --------------------------------------------------------------------
	//Water = new G4Material("Water", 1 * g/cm3, 2);
	//Water->AddElement(elH, 2);
	//Water->AddElement(elO, 1);

	// Liquid water at 20 degC with hydrogen bound in the molecular medium
	// (S(alpha,beta) thermal-scattering law, see G4MPhysicsList).  Using
	// G4_WATER or plain elH here would leave H under the free-gas elastic
	// treatment below 4 eV.  A dedicated material is used because G4_WATER
	// also has the nominal Geant4 density 1.0 g/cm3 rather than 0.99820 g/cm3.
	Water = new G4Material("Water_TS_H_of_Water",
	                       WCDMediumDensity20C(0.0),
	                       2,
	                       kStateLiquid,
	                       293.15 * kelvin,
	                       1.0 * bar);
	Water->AddElement(elTSHWater, 2);
	Water->AddElement(elO, 1);


	// One complete optical table per active medium. RINDEX changes with NaCl;
	// ABSLENGTH and MIEHG are common baselines until concentration-dependent
	// measurements are available.
	waterPT1 = CreateWCDOpticalTable(pureWaterRefIndex);
	waterPT2 = waterPT1;  // backward-compatible alias
	G4MaterialPropertiesTable* saltyWater2p5PT =
		CreateWCDOpticalTable(saltyWater2p5RefIndex);
	G4MaterialPropertiesTable* saltyWater5PT =
		CreateWCDOpticalTable(saltyWater5RefIndex);
	G4MaterialPropertiesTable* saltyWater10PT =
		CreateWCDOpticalTable(saltyWater10RefIndex);

	Water->SetMaterialPropertiesTable(waterPT1);

	// --------------------------------------------------------------------
	// Saline water materials at 20 C
	// Convention: w_NaCl = m_NaCl / (m_H2O + m_NaCl).
	// elTSHWater (not elH) supplies hydrogen so every solution keeps the
	// bound-hydrogen S(alpha,beta) treatment used by pure water.
	// --------------------------------------------------------------------
	SaltyWater_2p5 = CreateSaltyWaterByFinalMassFraction(
		SaltyWaterName(0.025), 0.025, elTSHWater, elO, elNa, elCl,
		saltyWater2p5PT);

	SaltyWater_5 = CreateSaltyWaterByFinalMassFraction(
		SaltyWaterName(0.05), 0.05, elTSHWater, elO, elNa, elCl,
		saltyWater5PT);

	SaltyWater_10 = CreateSaltyWaterByFinalMassFraction(
		SaltyWaterName(0.10), 0.10, elTSHWater, elO, elNa, elCl,
		saltyWater10PT);

	// Backward-compatible default alias. Prefer explicit SaltyWater_2p5,
	// SaltyWater_5 or SaltyWater_10 in the detector geometry.
	SaltyWater = SaltyWater_10;


	// --------------------------------------------------------------------
	// Rocks
	// --------------------------------------------------------------------
	StdRock = SiO2;

	// --------------------------------------------------------------------
	// Plastic Scintillator Bars
	// --------------------------------------------------------------------

	// Scintillator material:
	ScinPlastic = new G4Material("ScinPlastic", 1.060 * g/cm3, 3);
	ScinPlastic->AddMaterial(Polystyrene, 98.7*perCent);
	ScinPlastic->AddMaterial(PPO, 1*perCent);
	ScinPlastic->AddMaterial(POPOP, 0.3*perCent);

	// Scintillator Coating - 15% TiO2 and 85% polystyrene by weight.
	ScinCoating = new G4Material("ScinCoating", 1.52 * g/cm3, 2);
	ScinCoating->AddMaterial(TiO2, 15*perCent);
	ScinCoating->AddMaterial(Polystyrene, 85*perCent);

	// Add scintillator property table
	scinPT = new G4MaterialPropertiesTable();
	scinPT->AddProperty("RINDEX", scinPhotonEnergy, scinRefIndex, scinArrEntries);
	scinPT->AddProperty("ABSLENGTH", scinPhotonEnergy, scinAbsLen, scinArrEntries);
	scinPT->AddProperty("FASTCOMPONENT", scinPhotonEnergy, scinFastComp, scinArrEntries);
	scinPT->AddProperty("SLOWCOMPONENT", scinPhotonEnergy, scinSlowComp, scinArrEntries);
	scinPT->AddConstProperty("SCINTILLATIONYIELD", fScintillationYield);
	scinPT->AddConstProperty("RESOLUTIONSCALE", 1);
	scinPT->AddConstProperty("FASTTIMECONSTANT", fScinFastTime);
	scinPT->AddConstProperty("SLOWTIMECONSTANT", fScinSlowTime);
	scinPT->AddConstProperty("YIELDRATIO", 1);
	ScinPlastic->SetMaterialPropertiesTable(scinPT);

	// Add optical skin properties of scintillator (coating)
	ScinOptSurf = new G4OpticalSurface("ScinOptSurf", glisur, ground, dielectric_metal, fExtrusionPolish);

	scinOptSurfPT = new G4MaterialPropertiesTable();
	scinOptSurfPT->AddProperty("REFLECTIVITY", scinPhotonEnergy, scinOptSurfRefIndex, scinArrEntries);
	scinOptSurfPT->AddProperty("EFFICIENCY", scinPhotonEnergy, scinOptSurfEff, scinArrEntries);
	ScinOptSurf->SetMaterialPropertiesTable(scinOptSurfPT);

	// --------------------------------------------------------------------
	// PMMA (for WLS fibers)
	// --------------------------------------------------------------------
	

	PMMA = new G4Material("PMMA", 1.190 * g/cm3, 3);
	PMMA->AddElement(elC, 5);
	PMMA->AddElement(elH, 8);
	PMMA->AddElement(elO, 2);

	// Add properties to table
	pmmaPT = new G4MaterialPropertiesTable();
	pmmaPT->AddProperty("RINDEX", scinPhotonEnergy, pmmaRefIndex, scinArrEntries);
	pmmaPT->AddProperty("WLSABSLENGTH", scinPhotonEnergy, pmmaAbsLen, scinArrEntries);
	pmmaPT->AddProperty("WLSCOMPONENT", scinPhotonEnergy, pmmaEmission, scinArrEntries);
	pmmaPT->AddConstProperty("WLSTIMECONSTANT", fPMMADecayTime); // 
	PMMA->SetMaterialPropertiesTable(pmmaPT);

	/* WLS fibers are made of polymethylmethacrylate (PMMA)
		and a double cladding made of polyethylene and 
		fluorinated polyethylene

		PMMA: C5O2H8
		Pethylene: C2H4
	*/

	// Polyethylene (for internal cladding of WLS fibers)
	Pethylene = new G4Material("Pethylene", 1.200 * g/cm3, 2);
	Pethylene->AddElement(elC, 2);
	Pethylene->AddElement(elH, 4);

	// Add properties to table
	pethylenePT = new G4MaterialPropertiesTable();
	pethylenePT->AddProperty("RINDEX", scinPhotonEnergy, pethyRefIndex, scinArrEntries);
	pethylenePT->AddProperty("ABSLENGTH", scinPhotonEnergy, pethyAbsLen, scinArrEntries);
	Pethylene->SetMaterialPropertiesTable(pethylenePT);

	// Fluorinated Polyethylene (for external cladding of WLS fibers)
	FPethylene = new G4Material("FPethylene", 1.400 * g/cm3, 2);
	FPethylene->AddElement(elC, 2);
	FPethylene->AddElement(elH, 4);

	// Add properties to table
	fpethylenePT = new G4MaterialPropertiesTable();
	fpethylenePT->AddProperty("RINDEX", scinPhotonEnergy, fpethyRefIndex, scinArrEntries);
	fpethylenePT->AddProperty("ABSLENGTH", scinPhotonEnergy, pethyAbsLen, scinArrEntries);
	FPethylene->SetMaterialPropertiesTable(fpethylenePT);


	// --------------------------------------------------------------------
	// Effective absorbing PMT medium (keeps legacy material name "Pyrex")
	// --------------------------------------------------------------------
	/*
		This is not a resolved glass-window/vacuum/photocathode stack.  The
		ellipsoidal solid represents an effective photocathode: Fresnel losses
		are obtained from its RINDEX and photons that enter are absorbed.  The
		wavelength-dependent QE and collection efficiency are sampled exactly
		once by G4MPMTAction/OptDevice.  Do not also add EFFICIENCY here.
	*/

	// from PDG:
	// 80% SiO2 + 13% B2O2 + 7% Na2O
	// by fractional mass?

	Pyrex = new G4Material("Pyrex", 2.23 * g/cm3, 3);
	Pyrex->AddMaterial(SiO2, 0.80);
	Pyrex->AddMaterial(B2O2, 0.13);
	Pyrex->AddMaterial(Na2O, 0.07);

	// Optical properties for the effective PMT absorber.
	pyrexPT = new G4MaterialPropertiesTable();
	pyrexPT->AddProperty("RINDEX", pmtPhotonEnergy, pmtRefIndex, pmtArrEntries);
	pyrexPT->AddProperty("ABSLENGTH", pmtPhotonEnergy, pmtAbsLength, pmtArrEntries);
	Pyrex->SetMaterialPropertiesTable(pyrexPT);
	
	// --------------------------------------------------------------------
	// Tyvek / HDPE liner material for WCD
	// --------------------------------------------------------------------

	HDPE = new G4Material("Tyvek_HDPE", 0.94 * g/cm3, 2);
	HDPE->AddElement(elC, 2);
	HDPE->AddElement(elH, 4);

	// Bulk optical properties of Tyvek/HDPE
	linerPT1 = new G4MaterialPropertiesTable();

	linerPT1->AddProperty("RINDEX",
                      water1PhotonEnergy,
                      linerRefIndex,
                      water1ArrEntries);

	linerPT1->AddProperty("ABSLENGTH",
                      water1PhotonEnergy,
                      linerAbsLen,
                      water1ArrEntries);

	HDPE->SetMaterialPropertiesTable(linerPT1);


	// --------------------------------------------------------------------
	// Optical surface: water/salty water -> Tyvek
	// --------------------------------------------------------------------
	
	linerOpticalPT = new G4MaterialPropertiesTable();

	// Required by G4OpBoundaryProcess for a dielectric_dielectric
	// groundbackpainted surface. This describes the refractive index of the
	// optical coating at the active-medium -> Tyvek boundary.
	linerOpticalPT->AddProperty("RINDEX",
                            water1PhotonEnergy,
                            linerRefIndex,
                            water1ArrEntries);

	linerOpticalPT->AddProperty("REFLECTIVITY",
                            water1PhotonEnergy,
                            linerReflectivity,
                            water1ArrEntries);

	linerOpticalPT->AddProperty("BACKSCATTERCONSTANT",
                            water1PhotonEnergy,
                            linerBackScatter,
                            water1ArrEntries);

	linerOpticalPT->AddProperty("SPECULARLOBECONSTANT",
                            specularLobePhotonEnergy,
                            specularLobe,
                            3);

	linerOpticalPT->AddProperty("SPECULARSPIKECONSTANT",
                            specularLobePhotonEnergy,
                            specularSpike,
                            3);

	LinerOptSurf = new G4OpticalSurface("TyvekOpticalSurface");

	LinerOptSurf->SetModel(unified);
	LinerOptSurf->SetType(dielectric_dielectric);
	LinerOptSurf->SetFinish(groundbackpainted);
	LinerOptSurf->SetSigmaAlpha(fSigmaAlpha);
	LinerOptSurf->SetMaterialPropertiesTable(linerOpticalPT);

	// Alternate LAGO WCD liner surface (dielectric_LUT/groundtyvekair).  Not
	// used by SaltyWCD::BuildDetector, kept initialized for parity with other
	// detector models that may select it directly from Materials.
	LinerOptSurf2 = new G4OpticalSurface("WallSurface");
	LinerOptSurf2->SetType(dielectric_LUT);
	LinerOptSurf2->SetFinish(groundtyvekair);
	LinerOptSurf2->SetModel(LUT);




	// --------------------------------------------------------------------
	// Concrete
	// --------------------------------------------------------------------
	// 
	Concrete = new G4Material("Concrete", 2.5 *g/cm3, 6);
	Concrete->AddElement(elO, 0.52);
	Concrete->AddElement(elSi, 0.325);
	Concrete->AddElement(elCa, 0.06);
	Concrete->AddElement(elNa, 0.015);
	Concrete->AddElement(elFe, 0.04);
	Concrete->AddElement(elAl, 0.04);

	// define lead as material, not element
	Lead = new G4Material("Lead", 82., 207.2 * g/mole, 11.35 * g/cm3);
}
