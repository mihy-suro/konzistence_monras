#==============================================================================
# knihovny
#==============================================================================

library(readxl)
library(tolerance)
library("EnvStats")
library(RColorBrewer)
library(vioplot)


#==============================================================================
# pomocná filtrovací funkce
# filtruje data z datasertu podle zadaných kritérií
#==============================================================================
ff<-function(df,kom, om, lab, rn, start, end){
  if(kom == 0){kom<-df$kom}
  if(om == 0){om<-df$om}
  if(lab == 0){lab<-df$lab}
  if(start==0){start<-min(df$od)}
  if(end==0){end<-max(df$od)}
  if(rn==0){rn<-df$rn}
  f<-which(df$kom==kom & df$om==om & df$lab==lab & df$od>=start & df$od<=end & df$rn==rn)
  
  return(df[f,])
}
#==============================================================================
# Naètení dat
#==============================================================================
# cesta ke zdrojovému datasetu
ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../data/")
getwd()
data <- read_excel("./Polozky_PR/Smíšená strava 2023.xlsx", sheet=2, guess_max=21474836)

# ID monitorované položky
kom_ID<-data$ID_Monit_položka_OM 
# komodita
kom<-trimws(sapply(strsplit(data$Monitorovaná_položka_OM,"/"), tail, 1))
# odbìrové místo
om<-data$Odbìrové_místo
# ID odbìrového místa
om_ID<-data$ID_OM
# dodavatel dat (laboratoø)
lab<-data$Dodavatel_dat
# hodnota aktivity
a<-data$Hodnota
# hodnota nejistoty aktivity
u<-data$Nejistota
# jednotka
jed<-data$Jednotka
# MVA
mva<-data$Pod_MVA
# datum odbìru OD
od<-as.POSIXct(data$Datum_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
# datum odbìru DO
do<-as.POSIXct(data$Konec_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
# Radionuklid
rn<-data$Nuklid

# všechny parametry slouèeny do jednoho dataframe - tmpdf
tmpdf<-data.frame(kom_ID,kom, om, om_ID, lab, a, u, mva, jed, od, do, rn, stringsAsFactors=FALSE)

#==============================================================================
# Filtr pro Cs-137 a Sr-90
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


# filtrování dat pro analýzu (0 = všechny hodnoty)
kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do
rn = "Cs 137"       # radionuklid


# dataframe se všemi filtrovanými daty
allcs<-ff(tmpdf,kom, om, lab, rn, start, end)
# dataframe s novými daty
newcs<-allcs[which(allcs$od>newdata),]
# dataframe se starými daty
oldcs<-allcs[which((allcs$od<=newdata)&(allcs$od>olddata)),]
# Dataframe se starými i novými daty novìjšími než old data
newoldcs<-allcs[which(allcs$od>olddata),]


# filtrace pro Sr-90
rn = "Sr 90"       # radionuklid
allsr<-ff(tmpdf,kom, om, lab, rn, start, end)
newsr<-allsr[which(allsr$od>newdata),]
oldsr<-allsr[which((allsr$od<=newdata)&(allsr$od>olddata)),]
newoldsr<-allsr[which(allsr$od>olddata),]

# nastavení relativní cesty k adresáøi pro uložení obrázkù
ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
getwd()
setwd("../reports/smisena_strava/")

#==============================================================================
# Boxplot Cs-137 - všechny kraje
#==============================================================================

yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4))

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))
kssr <- ks.test(oldsr$a,newsr$a)
statssr<-paste("D-statistika = ",signif(as.numeric(kssr[1]),4),";  p-hodnota = ",signif(as.numeric(kssr[2]),4))

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("smisena_strava__boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/den]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 1.5, cex.axis=1.5, cex=1.5)
# stripchart(newoldcs$a ~ yearcs, vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvacs$a ~ yearmvacs, vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscs, side=3, line=0, cex=1.5)


if(kssr$p.value>0.05){colnew<-"green"}
if(kssr$p.value<=0.05){colnew<-"red"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

boxplot(newoldsr$a ~ yearsr, outline = FALSE,ylab="aktivita [Bq/den]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 1.5, cex.axis=1.5, cex=1.5)
# stripchart(newoldsr$a ~ yearsr, vertical = TRUE, data = newoldsr, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# if (length(newoldmvasr$a)>0){
# stripchart(newoldmvasr$a ~ yearmvasr, vertical = TRUE, data = newoldsr, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)}
mtext(statssr, side=3, line=0, cex=1.5)

dev.off()
####################################


#==============================================================================
# Scatterplot Cs-137 + Sr-90 - jednotlivé kraje
#==============================================================================

group_om <- as.factor(newoldcs$om)
oms<-levels(group_om)
nom <- length(oms)

for (i in 1:nom){
  omindcs <- which(newoldcs$om==oms[i])
  oldomscs <- which(oldcs$om==oms[i])
  ti90cs<-normtol.int(oldcs$a[oldomscs], alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
  ti95cs<-normtol.int(oldcs$a[oldomscs], alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
  ti99cs<-normtol.int(oldcs$a[oldomscs], alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
  limitscs <- paste("Cs-137 Lokalita: ",oms[i],"  Prùmìr = ", signif(mean(oldcs$a[oldomscs]),3),";  TI90 = ",signif(ti90cs[5],3),";  TI95 = ",signif(ti95cs[5],3), ";  TI99 = ",signif(ti99cs[5],3),sep="")
  
  omindsr <- which(newoldsr$om==oms[i])
  oldomssr <- which(oldsr$om==oms[i])
  ti90sr<-normtol.int(oldsr$a[oldomssr], alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
  ti95sr<-normtol.int(oldsr$a[oldomssr], alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
  ti99sr<-normtol.int(oldsr$a[oldomssr], alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
  limitssr <- paste("Sr-90 Lokalita: ",oms[i],"   Prùmìr = ", signif(mean(oldsr$a[oldomssr]),3),";  TI90 = ",signif(ti90sr[5],3),";  TI95 = ",signif(ti95sr[5],3), ";  TI99 = ",signif(ti99sr[5],3),sep="")
  
  ########################################################################
  omfile=gsub(" ", "", oms[i], fixed = TRUE)
  pngfile = paste("smisena_strava_",oms[i],".png",sep="")
  png(filename=pngfile,width = 1100, height = 1000, units = "px")
  
  par(mfrow=c(2,1), mai = c(1, 1, 1, 0.35))
  
  # mvaindcs<-which(newoldcs$mva[omindcs]==1)
  # plot(newoldcs$od[omindcs],newoldcs$a[omindcs],col= "black", 
  #      pch = 20, xlab="Datum", ylab="Aktivita [Bq/kg]", ylim=c(0,max(ti90cs[5],newoldcs$a[omindcs])),
  #      cex=3, cex.lab=2, cex.axis=2)
  # points(newoldcs$od[omindcs][mvaindcs],newoldcs$a[omindcs][mvaindcs],col= "green", pch=20, cex=3)
  # abline(h=ti90cs[5], col = "blue")
  # abline(h=ti95cs[5],col = "orange")
  # abline(h=ti99cs[5], col = "red")
  # mtext(limitscs, side=3, line=0, cex=2)
  
  
  newoldcs$od <- as.Date(newoldcs$od)
  
  # Your existing plotting code with the correction for date format
  mvaindcs <- which(newoldcs$mva[omindcs] == 1)
  plot(newoldcs$od[omindcs], newoldcs$a[omindcs], col= "black", pch = 20, xlab="Datum", ylab="Aktivita [Bq/kg]", ylim=c(0, max(ti90cs[5], newoldcs$a[omindcs])), cex=3, cex.lab=2, cex.axis=2, xaxt="n")
  axis.Date(side=1, at=seq(min(newoldcs$od[omindcs]), max(newoldcs$od[omindcs]), by="year"), format="%Y")
  points(newoldcs$od[omindcs][mvaindcs], newoldcs$a[omindcs][mvaindcs], col= "green", pch=20, cex=3)
  abline(h=ti90cs[5], col = "blue")
  abline(h=ti95cs[5], col = "orange")
  abline(h=ti99cs[5], col = "red")
  mtext(limitscs, side=3, line=0, cex=2)
  
  newoldsr$od <- as.Date(newoldsr$od)
  mvaindsr<-which(newoldsr$mva[omindsr]==1)
  plot(newoldsr$od[omindsr],newoldsr$a[omindsr],col= "black", 
       pch = 20, xlab="Datum", ylab="Aktivita [Bq/kg]", ylim=c(0,max(ti90sr[5],newoldsr$a[omindsr])),
       cex=3, cex.lab=2, cex.axis=2, xaxt="n")
  axis.Date(side=1, at=seq(min(newoldsr$od[omindsr]), max(newoldsr$od[omindsr]), by="year"), format="%Y")
  points(newoldsr$od[omindcs][mvaindsr],newoldcs$a[omindsr][mvaindsr],col= "green", pch=20, cex=3)
  abline(h=ti90sr[5], col = "blue")
  abline(h=ti95sr[5],col = "orange")
  abline(h=ti99sr[5], col = "red")
  mtext(limitssr, side=3, line=0, cex=2)

  dev.off()
  ########################################################
}

#==============================================================================
# Cs-137 lognormální qqplot s vyznaèenými aktuálními daty (necenzorovaná verze)
#==============================================================================

pngfile = paste("smisena_strava_qqplot_Cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

qqcs<-qqPlot(newoldcs$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newoldcs$typ<-"old"
newoldcs$typ[which(newoldcs$do>newdata)]<-"new"

dftypcs <-data.frame(a=newoldcs$a,typ=newoldcs$typ)
dfsortedcs <- dftypcs[order(dftypcs$a),] 
indnewcs<-which(dfsortedcs$typ=="new")

plot(qqcs$x,qqcs$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita [Bq/kg])", 
     pch=1, cex=2, cex.axis=2, cex.lab=2)
points(qqcs$x[indnewcs],qqcs$y[indnewcs],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0, cex=3)
abline(mean(qqcs$y), sd(qqcs$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
dev.off()


#==============================================================================
# Sr-90 lognormální qqplot s vyznaèenými aktuálními daty (necenzorovaná verze)
#==============================================================================

pngfile = paste("smisena_strava_qqplot_Sr90.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

qqsr<-qqPlot(newoldsr$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newoldsr$typ<-"old"
newoldsr$typ[which(newoldsr$do>newdata)]<-"new"

dftypsr <-data.frame(a=newoldsr$a,typ=newoldsr$typ)
dfsortedsr <- dftypsr[order(dftypsr$a),] 
indnewsr<-which(dfsortedsr$typ=="new")

plot(qqsr$x,qqsr$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita [Bq/kg])", 
     pch=1, cex=2, cex.axis=2, cex.lab=2)
points(qqsr$x[indnewsr],qqsr$y[indnewsr],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0, cex=3)
abline(mean(qqsr$y), sd(qqsr$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
dev.off()