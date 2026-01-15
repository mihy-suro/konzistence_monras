library(readxl)
library(tolerance)
library("EnvStats")
library(RColorBrewer)
library(vioplot)

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

data <- read_excel("./polozky_ZP/Voda povrchová 2023.xlsx", sheet=2, guess_max=21474836)

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

#==============================================================================
# Cs-137
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"


kom = 0             # komodita
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

rn = "H 3"       # radionuklid
allh<-ff(tmpdf,kom, om, lab, rn, start, end)
newh<-allh[which(allh$od>newdata),]
oldh<-allh[which((allh$od<=newdata)&(allh$od>olddata)),]
newoldh<-allh[which(allh$od>olddata),]


ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/povrchova_voda/")


newcs[newcs$lab2=="VÚV",]

#==============================================================================
# Casova rad Bysov
#==============================================================================
pngfile = paste("bysov.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

bysov_om<-unique(newoldcs$om[grepl("Býšov", newoldcs$om, ignore.case=FALSE)])
bysov<-subset(newoldcs, subset = om %in% bysov_om)
aind<-which(bysov$mva==0)
mvaind<-which(bysov$mva==1)

plot(bysov$od[mvaind],bysov$a[mvaind], col= "green", pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,0.35))
points(bysov$od[aind],bysov$a[aind], col= 1, pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

dev.off()

#==============================================================================
# Boxplot vuv + suro
#==============================================================================

yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("Povrchová voda - Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4))

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))
kssr <- ks.test(oldsr$a,newsr$a)
statssr<-paste("Povrchová voda - Sr-90 D-statistika = ",signif(as.numeric(kssr[1]),4),";  p-hodnota = ",signif(as.numeric(kssr[2]),4))

yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldh[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))
ksh <- ks.test(oldh$a,newh$a)
statsh<-paste("Povrchová voda - H-3 D-statistika = ",signif(as.numeric(ksh[1]),4),";  p-hodnota = ",signif(as.numeric(ksh[2]),4))


colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("povrchova_voda__boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

par(mfrow=c(3,1), mai = c(1, 1, 1, 0.1))

if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(newoldcs$mva==0)
boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldcs$a[aind] ~ yearcs[aind], vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvacs$a ~ yearmvacs, vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscs, side=3, line=0, cex=2)


if(kssr$p.value<=0.05){colnew<-"red"}
if(kssr$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

aind<-which(newoldsr$mva==0)
boxplot(newoldsr$a ~ yearsr, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldsr$a[aind] ~ yearsr[aind], vertical = TRUE, data = newoldsr, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# if (length(newoldmvasr$a)>0){
#   stripchart(newoldmvasr$a ~ yearmvasr, vertical = TRUE, data = newoldsr, 
#              method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)}
mtext(statssr, side=3, line=0, cex=2)

if(ksh$p.value<=0.05){colnew<-"red"}
if(ksh$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearh))-1),colnew)

aind<-which(newoldh$mva==0)
boxplot(newoldh$a ~ yearh, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldh$a[aind] ~ yearh[aind], vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# if (length(newoldmvah$a)>0){
#   stripchart(newoldmvah$a ~ yearmvah, vertical = TRUE, data = newoldh, 
#              method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)}
mtext(statsh, side=3, line=0, cex=2)

dev.off()
####################################




#==============================================================================
# Boxplot Cs-137
#==============================================================================

yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
newoldcs$year <- yearcs

bxsuro <- newoldcs[which(newoldcs$lab=="SÚRO"),]
bxsuromva <- bxsuro[which(bxsuro$mva==1),]

bxvuv <- newoldcs[which(newoldcs$lab=="VÚV"),]
bxvuvmva <- bxvuv[which(bxvuv$mva==1),]

bxete <- newoldcs[which(newoldcs$lab=="ETE"),]
bxetemva <- bxvuv[which(bxete$mva==1),]

newind <- which(bxsuro$od>newdata)
kscssuro <- ks.test(bxsuro$a,bxsuro$a[newind])
statscssuro<-paste("Povrchová voda - SÚRO Cs-137 D-statistika = ",signif(as.numeric(kscssuro[1]),4),";  p-hodnota = ",signif(as.numeric(kscssuro[2]),4))

newind <- which(bxvuv$od>newdata)
kscsvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statscsvuv<-paste("Povrchová voda - VÚV Cs-137 D-statistika = ",signif(as.numeric(kscsvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kscsvuv[2]),4))

newind <- which(bxete$od>newdata)
kscsete <- ks.test(bxete$a,bxete$a[newind])
statscsete<-paste("Povrchová voda - ETE Cs-137 D-statistika = ",signif(as.numeric(kscsete[1]),4),";  p-hodnota = ",signif(as.numeric(kscsete[2]),4))


pngfile = paste("povrchova_voda__boxplot_cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 1300, units = "px")

par(mfrow=c(3,1), mai = c(1, 1, 1, 0.1))

if(kscssuro$p.value<=0.05){colnew<-"red"}
if(kscssuro$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(bxsuro$mva==0)
boxplot(bxsuro$a ~ bxsuro$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxsuro$a[aind] ~ bxsuro$year[aind], vertical = TRUE, data = bxsuro, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxsuromva$a ~ bxsuromva$year, vertical = TRUE, data = bxsuromva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscssuro, side=3, line=0, cex=2)


if(kscsvuv$p.value<=0.05){colnew<-"red"}
if(kscsvuv$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(bxvuv$mva==0)
boxplot(bxvuv$a ~ bxvuv$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxvuv$a[aind] ~ bxvuv$year[aind], vertical = TRUE, data = bxvuv, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxvuvmva$a ~ bxvuvmva$year, vertical = TRUE, data = bxvuvmva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscsvuv, side=3, line=0, cex=2)


if(kscsete$p.value<=0.05){colnew<-"red"}
if(kscsete$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(bxete$mva==0)
boxplot(bxete$a ~ bxete$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxete$a[aind] ~ bxete$year[aind], vertical = TRUE, data = bxete, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxetemva$a ~ bxetemva$year, vertical = TRUE, data = bxetemva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscsete, side=3, line=0, cex=2)

dev.off()



#==============================================================================
# Boxplot Sr-90
#==============================================================================

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))

newoldsr$year <- yearsr

bxvuv <- newoldsr[which(newoldsr$lab=="VÚV"),]
bxvuvmva <- bxvuv[which(bxvuv$mva==1),]

newind <- which(bxvuv$od>newdata)
kssrvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statssrvuv<-paste("Povrchová voda - VÚV Sr-90 D-statistika = ",signif(as.numeric(kssrvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kssrvuv[2]),4))


pngfile = paste("povrchova_voda__boxplot_sr90.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

par(mfrow=c(1,1), mai = c(1, 1, 1, 0.1))

if(kssrvuv$p.value<=0.05){colnew<-"red"}
if(kssrvuv$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(bxvuv$mva==0)
boxplot(bxvuv$a ~ bxvuv$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxvuv$a[aind] ~ bxvuv$year[aind], vertical = TRUE, data = bxvuv, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxvuvmva$a ~ bxvuvmva$year, vertical = TRUE, data = bxvuvmva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statssrvuv, side=3, line=0, cex=2)

dev.off()


#==============================================================================
# Boxplot H-3
#==============================================================================

yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldsr[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))

newoldh$year <- yearh

bxsuro <- newoldh[which(newoldh$lab=="SÚRO"),]
bxsuromva <- bxsuro[which(bxsuro$mva==1),]
bxvuv <- newoldh[which(newoldh$lab=="VÚV"),]
bxvuvmva <- bxvuv[which(bxvuv$mva==1),]

newind <- which(bxsuro$od>newdata)
kshsuro <- ks.test(bxsuro$a,bxsuro$a[newind])
statshsuro<-paste("Povrchová voda - SÚRO H-3  D-statistika = ",signif(as.numeric(kshsuro[1]),4),";  p-hodnota = ",signif(as.numeric(kshsuro[2]),4))
newind <- which(bxvuv$od>newdata)
kshvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statshvuv<-paste("Povrchová voda - VÚV H-3  D-statistika = ",signif(as.numeric(kshvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kshvuv[2]),4))


pngfile = paste("povrchova_voda__boxplot_H3.png",sep="")
png(filename=pngfile,width = 1100, height = 1300, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

if(kshsuro$p.value<=0.05){colnew<-"red"}
if(kshsuro$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

aind<-which(bxsuro$mva==0)
boxplot(bxsuro$a ~ bxsuro$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxsuro$a[aind] ~ bxsuro$year[aind], vertical = TRUE, data = bxsuro, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxsuromva$a ~ bxsuromva$year, vertical = TRUE, data = bxsuromva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statshsuro, side=3, line=0, cex=2)


if(kshvuv$p.value<=0.05){colnew<-"red"}
if(kshvuv$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(bxvuv$mva==0)
boxplot(bxvuv$a ~ bxvuv$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxvuv$a[aind] ~ bxvuv$year[aind], vertical = TRUE, data = bxvuv, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxvuvmva$a ~ bxvuvmva$year, vertical = TRUE, data = bxvuvmva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statshvuv, side=3, line=0, cex=2)

dev.off()



# poèet hodnot H3, které pøevyšují 2 Bq/L
HDF = tmpdf[tmpdf$rn =="H 3",]
H3high <- HDF[HDF$a>2 & HDF$mva==0,]
table(H3high$lab)




#==============================================================================
# Cs-137 èasová øada s rozlišením laborek
#==============================================================================
library(randomcoloR)

group <- as.factor(newoldcs$lab)
labs<-levels(group)
nlab <- length(labs)

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}

ti90<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste(" Povrchová voda Cs-137 Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldcs$lab==labs[1])

pngfile = paste("povrchova_voda_rada_cs137.png",sep="")
png(filename=pngfile,width = 1000, height = 700, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 10.5))

mvaind<-which(newoldcs$mva[labind]==1)
aind<-which(newoldcs$mva[labind]==0)
plot(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col= "green", pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,as.numeric(ti99[5]*1.1)))
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
  points(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col = "green", pch=19, cex=1.5)
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
# Sr-90 èasová øada s rozlišením laborek
#==============================================================================
library(randomcoloR)

group <- as.factor(newoldsr$lab)
labs<-levels(group)
nlab <- length(labs)

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}

ti90<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste(" Povrchová voda Sr-90 Prùmìr = ", signif(mean(newoldsr$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldsr$lab==labs[1])

pngfile = paste("povrchova_voda_rada_sr90.png",sep="")
png(filename=pngfile,width = 1000, height = 700, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 10.5))

mvaind<-which(newoldsr$mva[labind]==1)
aind<-which(newoldsr$mva[labind]==0)
plot(newoldsr$od[labind][mvaind],newoldsr$a[labind][mvaind], col= "green", pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,as.numeric(ti99[5]*1.1)))
points(newoldsr$od[labind][aind],newoldsr$a[labind][aind], col= colors[1], pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)

for (i in 2:nlab){
  labind <-which(newoldsr$lab==labs[i])
  mvaind<-which(newoldsr$mva[labind]==1)
  aind<-which(newoldsr$mva[labind]==0)
  points(newoldsr$od[labind][mvaind],newoldsr$a[labind][mvaind], col = "green", pch=19, cex=1.5)
  points(newoldsr$od[labind][aind],newoldsr$a[labind][aind], col = colors[i], pch=19, cex=1.5)
  
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
# H-3 èasová øada s rozlišením laborek
#==============================================================================
group <- as.factor(newoldh$lab)
labs<-levels(group)
nlab <- length(labs)

colors_user <- c(rgb(0,1,1,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4), rgb(1,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}

ti90<-normtol.int(newoldh$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldh$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldh$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Povrchová voda H-3 Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldh$lab==labs[1])

pngfile = paste("povrchova_voda_rada_h3.png",sep="")
png(filename=pngfile,width = 1000, height = 700, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 10.5))

mvaind<-which(newoldh$mva[labind]==1)
aind<-which(newoldh$mva[labind]==0)

plot(newoldh$od[labind][aind],newoldh$a[labind][aind], col= colors[1], pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,as.numeric(ti99[5])))
points(newoldh$od[labind][mvaind],newoldh$a[labind][mvaind], col= "green", pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)

for (i in 2:nlab){
  labind <-which(newoldh$lab==labs[i])
  mvaind<-which(newoldh$mva[labind]==1)
  aind<-which(newoldh$mva[labind]==0)
  points(newoldh$od[labind][mvaind],newoldh$a[labind][mvaind], col = "green", pch=19, cex=1.5)
  points(newoldh$od[labind][aind],newoldh$a[labind][aind], col = colors[i], pch=19, cex=1.5)
  
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
# QQPLOT
#==============================================================================
pngfile = paste("povrchova_voda_qqplot_Cs137.png",sep="")
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
mtext("Povrchová voda - Cs-137", side=3, line=0, cex=2)
dev.off()


pngfile = paste("povrchova_voda_qqplot_Sr90.png",sep="")
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
mtext("Povrchová voda - Sr-90", side=3, line=0, cex=2)
dev.off()

pngfile = paste("povrchova_voda_qqplot_H3.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

qqh<-qqPlot(newoldh$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newoldh$typ<-"old"
newoldh$typ[which(newoldh$do>newdata)]<-"new"

dftyph <-data.frame(a=newoldh$a,typ=newoldh$typ)
dfsortedh <- dftyph[order(dftyph$a),] 
indnewh<-which(dfsortedh$typ=="new")

plot(qqh$x,qqh$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita [Bq/L])", 
     pch=1, cex=2, cex.axis=2, cex.lab=2)
points(qqh$x[indnewh],qqh$y[indnewh],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0, cex=3)
abline(mean(qqh$y), sd(qqh$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=2)
mtext("Povrchová voda - H-3", side=3, line=0, cex=2)
dev.off()


