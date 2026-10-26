# flujo por longitud de traza en el agua, por componente: bins de log10(E/MeV) de -9.5 a -3.5, 0.02 de ancho
BEGIN{FS="\t"; while((getline l < COMP)>0){comp[n++]=l+0}; nb=300; lo=-9.5; w=0.02}
/^#/{next}
$9 ~ /Water/ {
  e=$16+0; if(e<=0) next; le=log(e)/log(10); b=int((le-lo)/w); if(b<0||b>=nb) next
  dx=$13-$10; dy=$14-$11; dz=$15-$12; L=sqrt(dx*dx+dy*dy+dz*dz)
  k=comp[$1+0]; F[k,b]+=L; N[k,b]++
}
END{for(k=1;k<=3;k++) for(b=0;b<nb;b++) printf "%d\t%.4f\t%.6g\t%d\n", k, lo+(b+0.5)*w, F[k,b]+0, N[k,b]+0}
