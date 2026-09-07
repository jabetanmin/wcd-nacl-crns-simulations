#!/bin/bash
# generate file with particle information 
# will generate "n" particles, with id "pid" for each momentum and angle given 
if [ -z "$1" ] ; then
  echo "need number of particles to be generated!"
  exit 1
fi

if [ -z "$2" ] ; then
  echo "need particle Id! (CORSIKA)"
  exit 1
fi


n="$1"
pid="$2"

awk '
BEGIN {
  pi = 4*atan2(1, 1)
  rad = pi / 180
  GeV = 1 / 1000
  n = '$n'
  pid = '$pid'
  #momentum = "3e-1 4e-1 5e-1 6e-1 7e-1 8e-1 9e-1 10e-1"
  #momentum = "1.09067181" # in GeV
  #momentum = "0.00000685406" # 25meV-in GeV
  #momentum = "0.000043348933" # 1eV-in GeV
  #momentum = "0.000036268320" # 0.7eV-in GeV
  #momentum = "0.000030652326" # 0.5eV-in GeV
  #momentum = "0.000023743191" # 0.3eV-in GeV
  #momentum = "0.000013708134" # 0.1eV-in GeV
  #momentum = "0.000012260928" # 0.08eV-in GeV
  #momentum = "0.0000096931209" # 0.05eV-in GeV
  momentum = "0.0000013708134" # 0.001eV-in GeV
  #momentum = "0.0000043348933" # 0.01eV-in GeV
  #momentum = "0.0000036268320" # 0.007eV-in GeV
  #momentum = "0.0000030652326" # 0.007eV-in GeV
  #momentum = "0.0000021674464" # 0.007eV-in GeV
  #momentum = "0.0043349048" # 1KeV-in GeV
  #momentum = "0.04336046" # 1MeV-in GeV
  #momentum = "1.090671811" # 500MeV
  #momentum = "0.00009693116" # 5eV
  #momentum = "0.0001370813" # 10eV
  #momentum = "0.00016788969" # 15eV
  #momentum = "0.0003065232495" # 50eV
  #momentum = "0.0004334893424" # 100eV
  #momentum = "0.000530913856" # 150eV
  #momentum = "0.000685406859" # 250eV
  #momentum = "0.00096931174" # 500eV
  #momentum = "0.001370813991" # 1000eV
  #momentum = "0.003065236532" # 5000eV
  #momentum = "0.003754135220" # 7500eV
  #momentum = "0.004334904843" # 10000eV
  #momentum = "0.0137085010121" # 100000eV
  #momentum = "0.021675908285" # 250KeV
  #momentum = "0.03065640226" # 500KeV
  #momentum = "0.037548768288" # 750KeV
  #momentum = "0.0433604658646" # 1MeV
  #momentum = "0.1374456256124" # 10MeV
  #momentum = "0.16855844683" # 15MeV
  #momentum = "0.4448741395046" # 100MeV
  #momentum = "0.808541279094" # 300MeV
  split(momentum, p, " ")
  for (pi = 1; pi <= length(p); ++pi) {
    angles = "0"
    split(angles, a, " ")
    for (ai = 1; ai <= length(a); ++ai) {
      th = a[ai]*rad
      phi = rand()*2*pi
      px = p[pi]*sin(th)*cos(phi)
      py = p[pi]*sin(th)*sin(phi)
      pz = p[pi]*cos(th)
      for (i = 0; i < n; ++i)
      print pid, px, py, pz, 0, 0, 0, 0, 0, 0, 0, 0
    }
  }
}
'
