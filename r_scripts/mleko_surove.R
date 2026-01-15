# install.packages("rstudioapi")

library(readxl)
library(tolerance)
library(EnvStats)
library(RColorBrewer)
library(vioplot)
library(rstudioapi)

#==============================================================================
# pomocná filtrovací funkce
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
ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../data/")

data <- read_excel("./Polozky_PR/Mléko 2023.xlsx", sheet=2, guess_max=21474836)

kom_ID<-data$ID_Monit_položka_OM 
kom<-trimws(sapply(strsplit(data$Monitorovaná_položka_OM,"/"), tail, 1))
om<-data$Odbìrové_místo
om_ID<-data$ID_OM
lab<-data$Dodavatel_dat
a<-data$Hodnota
u<-data$Nejistota
jed<-data$Jednotka
mva<-data$Pod_MVA
od<-as.POSIXct(data$Datum_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
do<-as.POSIXct(data$Konec_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
rn<-data$Nuklid
tmpdf<-data.frame(kom_ID,kom, om, om_ID, lab, a, u, mva, jed, od, do, rn, stringsAsFactors=FALSE)

# nahradit RC za SÚRO:
tmpdf$lab2 <- tmpdf$lab
tmpdf$lab[grepl("RC", tmpdf$lab, ignore.case=FALSE)] <- "SÚRO"
tmpdf$lab[grepl("SÚJB", tmpdf$lab, ignore.case=FALSE)] <- "SÚRO"

mkonz<-"mléko kravské - konzumní"
msur<-"mléko kravské - surové"
mleko<-"mléko"

msus<-"mléko sušené"

movc<-"mléko ovèí"
mkoz<-"mléko kozí"
mzak<-"mléko zakysané"

tmpdf$kom[tmpdf$kom==mkonz]<-"mkonz"
tmpdf$kom[tmpdf$kom==msur]<-"msur"
tmpdf$kom[tmpdf$kom==msus]<-"msus"
tmpdf$kom[tmpdf$kom==mleko]<-"mleko"
tmpdf$kom[tmpdf$kom==movc]<-"most"
tmpdf$kom[tmpdf$kom==mkoz]<-"most"
tmpdf$kom[tmpdf$kom==mzak]<-"most"

#==============================================================================
# Mléko surové Cs-137 - Filtr
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2012-01-01 00:00:00 CET"

kom = "msur"         # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "Cs 137"       # radionuklid
allcs<-ff(tmpdf,kom, om, lab, rn, start, end)
newcs<-allcs[which(allcs$od>newdata),]
oldcs<-allcs[which((allcs$od<=newdata)&(allcs$od>olddata)),]
newoldcs<-allcs[which(allcs$od>olddata),]

rn = "Sr 90"       # radionuklid
allsr<-ff(tmpdf,kom, om, lab, rn, start, end)
newsr<-allsr[which(allsr$od>newdata),]
oldsr<-allsr[which((allsr$od<=newdata)&(allsr$od>olddata)),]
newoldsr<-allsr[which(allsr$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/mleko/")

#==============================================================================
# Boxplot mléko surove
#==============================================================================
yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("Mléko surové - Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4)) 

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))
kssr <- ks.test(oldsr$a,newsr$a)
statssr<-paste("Mléko surové - Sr-90 D-statistika = ",signif(as.numeric(kssr[1]),4),";  p-hodnota = ",signif(as.numeric(kssr[2]),4))

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("mleko_surove__boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# Cs-137 graf
if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
mtext(statscs, side=3, line=0, cex=2)

# Sr-90 graf
if(kssr$p.value<=0.05){colnew<-"red"}
if(kssr$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

boxplot(newoldsr$a ~ yearsr, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
mtext(statssr, side=3, line=0, cex=2)


dev.off()





#==============================================================================
# Boxplot Cs-137 - podle laborek
#==============================================================================

yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
newoldcs$year <- yearcs

bxsuro <- newoldcs[which(newoldcs$lab=="SÚRO"),]
bxsuromva <- bxsuro[which(bxsuro$mva==1),]

bxsvu <- newoldcs[which(newoldcs$lab=="SVÚ"),]
bxsvumva <- bxsvu[which(bxsvu$mva==1),]

bxete <- newoldcs[which(newoldcs$lab=="ETE"),]
bxetemva <- bxete[which(bxete$mva==1),]

bxsvu <- newoldcs[which(newoldcs$lab=="SVÚ"),]
bxsvumva <- bxsvu[which(bxsvu$mva==1),]

newind <- which(bxsuro$od>newdata)
kscssuro <- ks.test(bxsuro$a,bxsuro$a[newind])
statscssuro<-paste("SÚRO - surové mléko - Cs-137 D-statistika = ",signif(as.numeric(kscssuro[1]),4),";  p-hodnota = ",signif(as.numeric(kscssuro[2]),4))

newind <- which(bxsvu$od>newdata)
kscssvu <- ks.test(bxsvu$a,bxsvu$a[newind])
statscssvu<-paste("SVU - surové mléko - Cs-137 D-statistika = ",signif(as.numeric(kscssvu[1]),4),";  p-hodnota = ",signif(as.numeric(kscssvu[2]),4))

newind <- which(bxete$od>newdata)
kscsete <- ks.test(bxete$a,bxete$a[newind])
statscsete<-paste("ETE - surové mléko - Cs-137 D-statistika = ",signif(as.numeric(kscsete[1]),4),";  p-hodnota = ",signif(as.numeric(kscsete[2]),4))

# graf SURO + SVU
pngfile = paste("mleko_surove_cs137_SURO_SVU.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

if(kscssuro$p.value<=0.05){colnew<-"red"}
if(kscssuro$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(bxsuro$a ~ bxsuro$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
mtext(statscssuro, side=3, line=0, cex=2)


if(kscssvu$p.value<=0.05){colnew<-"red"}
if(kscssvu$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(bxsvu$a ~ bxsvu$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
mtext(statscssvu, side=3, line=0, cex=2)

dev.off()

#==============================================================================
# èasová øada podle dodavatele
#==============================================================================

group <- as.factor(newoldcs$lab)
labs<-levels(group)
nlab <- length(labs)

colors_user <- c("blue","black","red","orange")
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,randomcoloR::distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}

ti90<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Cs-137 Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldcs$lab==labs[1])

pngfile = paste("mleko_surove_rada_cs137.png",sep="")
png(filename=pngfile,width = 1000, height = 700, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 12))

yhigh=max(as.numeric(ti99[5])*1.1,max(newoldcs$a))

mvaind<-which(newoldcs$mva[labind]==1)
aind<-which(newoldcs$mva[labind]==0)
plot(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col= colors[1], pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,yhigh))
points(newoldcs$od[labind][aind],newoldcs$a[labind][aind], col= 1, pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)

for (i in 2:nlab){
  labind <-which(newoldcs$lab==labs[i])
  mvaind<-which(newoldcs$mva[labind]==1)
  aind<-which(newoldcs$mva[labind]==0)
  points(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col = colors[i], pch=19, cex=1.5)
  points(newoldcs$od[labind][aind],newoldcs$a[labind][aind], col = colors[i], pch=19, cex=1.5)
  
}


legend("topright",
       inset = c(-0.15, 0), 
       legend = labs, 
       col = colors,
       pch = 19,
       xpd = TRUE,
       cex=1.5) 

on.exit(par(opar))

dev.off()


#==============================================================================
# QQPLOT mléko surove
#==============================================================================
pngfile = paste("mleko_surove_qqplot_Cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

qqcs<-qqPlot(newoldcs$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newoldcs$typ<-"old"
newoldcs$typ[which(newoldcs$do>newdata)]<-"new"

dftypcs <-data.frame(a=newoldcs$a,typ=newoldcs$typ)
dfsortedcs <- dftypcs[order(dftypcs$a),] 
indnewcs<-which(dfsortedcs$typ=="new")

plot(qqcs$x,qqcs$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita [Bq/L])", 
     pch=1, cex=2, cex.axis=2, cex.lab=2)
points(qqcs$x[indnewcs],qqcs$y[indnewcs],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0, cex=3)
abline(mean(qqcs$y), sd(qqcs$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
mtext("Surové mléko - Cs-137", side=3, line=0, cex=2)
dev.off()


pngfile = paste("mleko_surove_qqplot_Sr90.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

qqsr<-qqPlot(newoldsr$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newoldsr$typ<-"old"
newoldsr$typ[which(newoldsr$do>newdata)]<-"new"

dftypsr <-data.frame(a=newoldsr$a,typ=newoldsr$typ)
dfsortedsr <- dftypsr[order(dftypsr$a),] 
indnewsr<-which(dfsortedsr$typ=="new")

plot(qqsr$x,qqsr$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita [Bq/L])", 
     pch=1, cex=2, cex.axis=2, cex.lab=2)
points(qqsr$x[indnewsr],qqsr$y[indnewsr],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0, cex=3)
abline(mean(qqsr$y), sd(qqsr$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
mtext("Surové mléko - Sr-90", side=3, line=0, cex=2)
dev.off()
