library(readxl)
library(tolerance)
library("EnvStats")
library(RColorBrewer)
library(vioplot)
library(randomcoloR)

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

data <- read_excel("./Polozky_ZP/Pitná voda 2023.xlsx", sheet=2, guess_max=21474836)

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
newoldh<-allh[which(allh$od>olddata),]

ind = which(newoldh$lab2=="VÚV" | newoldh$lab2=="SÚRO")
newoldh <- newoldh[ind,]


ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/pitna_voda/")





#==============================================================================
# Boxplot vuv + suro
#==============================================================================

yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4))

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))
kssr <- ks.test(oldsr$a,newsr$a)
statssr<-paste("Sr-90 D-statistika = ",signif(as.numeric(kssr[1]),4),";  p-hodnota = ",signif(as.numeric(kssr[2]),4))

yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldh[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))
ksh <- ks.test(oldh$a,newh$a)
statsh<-paste("H-3 D-statistika = ",signif(as.numeric(ksh[1]),4),";  p-hodnota = ",signif(as.numeric(ksh[2]),4))


colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("pitna_voda__boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

par(mfrow=c(4,1), mai = c(1, 1, 1, 0.1))

if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

aind<-which(newoldcs$mva==0)
boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldcs$a[aind] ~ yearcs[aind], vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvacs$a ~ yearmvacs, vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscs, side=3, line=0, cex=2)


boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2, ylim=c(0,0.0025))
# stripchart(newoldcs$a[aind] ~ yearcs[aind], vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvacs$a ~ yearmvacs, vertical = TRUE, data = newoldcs, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscs, side=3, line=0, cex=2)


if(kssr$p.value<=0.05){colnew<-"red"}
if(kssr$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

aind<-which(newoldsr$mva==0)
boxplot(newoldsr$a ~ yearsr, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
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
boxplot(newoldh$a ~ yearh, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
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

x = newoldcs[newoldcs$year==2023,]
x[x$mva==0,]

bxsuro <- newoldcs[which(newoldcs$lab=="SÚRO"),]
bxsuromva <- bxsuro[which(bxsuro$mva==1),]
bxvuv <- newoldcs[which(newoldcs$lab=="VÚV"),]
bxvuvmva <- bxvuv[which(bxvuv$mva==1),]

newind <- which(bxsuro$od>newdata)
kscssuro <- ks.test(bxsuro$a,bxsuro$a[newind])
statscssuro<-paste("SÚRO Cs-137 D-statistika = ",signif(as.numeric(kscssuro[1]),4),";  p-hodnota = ",signif(as.numeric(kscssuro[2]),4))
kscsvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statscsvuv<-paste("VÚV Cs-137 D-statistika = ",signif(as.numeric(kscsvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kscsvuv[2]),4))


pngfile = paste("pitna_voda__boxplot_cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

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

dev.off()



#==============================================================================
# Boxplot Sr-90
#==============================================================================

yearsr <- as.numeric(format(newoldsr$od,'%Y'))
newoldmvasr<-newoldsr[which(newoldsr$mva==1),]
yearmvasr <- as.numeric(format(newoldmvasr$od,'%Y'))

newoldsr$year <- yearsr

bxsuro <- newoldsr[which(newoldsr$lab=="SÚRO"),]
bxsuromva <- bxsuro[which(bxsuro$mva==1),]
bxvuv <- newoldsr[which(newoldsr$lab=="VÚV"),]
bxvuvmva <- bxvuv[which(bxvuv$mva==1),]

newind <- which(bxsuro$od>newdata)
kssrsuro <- ks.test(bxsuro$a,bxsuro$a[newind])
statssrsuro<-paste("SÚRO Sr-90 D-statistika = ",signif(as.numeric(kssrsuro[1]),4),";  p-hodnota = ",signif(as.numeric(kssrsuro[2]),4))
kssrvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statssrvuv<-paste("VÚV Sr-90 D-statistika = ",signif(as.numeric(kssrvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kssrvuv[2]),4))


pngfile = paste("pitna_voda__boxplot_sr90.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

if(kssrsuro$p.value<=0.05){colnew<-"red"}
if(kssrsuro$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearsr))-1),colnew)

aind<-which(bxsuro$mva==0)
boxplot(bxsuro$a ~ bxsuro$year, outline = FALSE,ylab="aktivita [Bq/L]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(bxsuro$a[aind] ~ bxsuro$year[aind], vertical = TRUE, data = bxsuro, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(bxsuromva$a ~ bxsuromva$year, vertical = TRUE, data = bxsuromva, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statssrsuro, side=3, line=0, cex=2)


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
statshsuro<-paste("SÚRO H-3  D-statistika = ",signif(as.numeric(kshsuro[1]),4),";  p-hodnota = ",signif(as.numeric(kshsuro[2]),4))
kshvuv <- ks.test(bxvuv$a,bxvuv$a[newind])
statshvuv<-paste("VÚV H-3  D-statistika = ",signif(as.numeric(kshvuv[1]),4),";  p-hodnota = ",signif(as.numeric(kshvuv[2]),4))


pngfile = paste("pitna_voda__boxplot_H3.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

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
group <- as.factor(newoldcs$lab)
labs<-levels(group)
labs<-c("SÚRO","VÚV")
nlab <- length(labs)

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4),rgb(0,1,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}

colors<-c("black","blue")

ti90<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Cs-137 Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldcs$lab==labs[1])

pngfile = paste("pitna_voda_rada_cs137.png",sep="")
png(filename=pngfile,width = 1000, height = 900, units = "px")

opar <- par(no.readonly = TRUE)
par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))
par(mar = c(6, 5, 4, 10.5))

yhigh<-max(as.numeric(ti99[5])*1.1,max(newoldcs$a)*1.1)
mvaind<-which(newoldcs$mva==1)
aind<-which(newoldcs$mva==0)

plot(newoldcs$od[mvaind],newoldcs$a[mvaind], col= "green", pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0, yhigh))
points(newoldcs$od[aind],newoldcs$a[aind], col= 1, pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)

for (i in 2:nlab){
  labind <-which(newoldcs$lab==labs[i])
  mvaind<-which(newoldcs$mva[labind]==0)
  aind<-which(newoldcs$mva[labind]==0)
  points(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col = "green", pch=19, cex=1.5)
  points(newoldcs$od[labind][aind],newoldcs$a[labind][aind], col = "blue", pch=19, cex=1.5)
  
  }


legend("topright",
       inset = c(-0.15, 0), 
       legend = labs, 
       col = colors,
       pch = 19,
       xpd = TRUE,
       cex=1.5) 





# zoom predchoziho
limits <- paste("Cs-137 (zoom) Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
yhigh<-max(as.numeric(ti99[5])*1.1,max(newoldcs$a)*1.1)
mvaind<-which(newoldcs$mva==1)
aind<-which(newoldcs$mva==0)

plot(newoldcs$od[mvaind],newoldcs$a[mvaind], col= "green", pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0, 0.025))
points(newoldcs$od[aind],newoldcs$a[aind], col= 1, pch = 19, 
       xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5)

abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=1.5)

for (i in 2:nlab){
  labind <-which(newoldcs$lab==labs[i])
  mvaind<-which(newoldcs$mva[labind]==0)
  aind<-which(newoldcs$mva[labind]==0)
  points(newoldcs$od[labind][mvaind],newoldcs$a[labind][mvaind], col = "green", pch=19, cex=1.5)
  points(newoldcs$od[labind][aind],newoldcs$a[labind][aind], col = "blue", pch=19, cex=1.5)
  
}


on.exit(par(opar))

dev.off()



#==============================================================================
# Sr-90 èasová øada s rozlišením laborek
#==============================================================================
group <- as.factor(newoldsr$lab)
labs<-levels(group)
nlab <- length(labs)
labs<-c("SÚRO","VÚV")

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}
colors<-c("black","blue")

ti90<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldsr$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Sr-90 Prùmìr = ", signif(mean(newoldsr$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldsr$lab==labs[1])

pngfile = paste("pitna_voda_rada_sr90.png",sep="")
png(filename=pngfile,width = 1000, height = 450, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 10.5))

mvaind<-which(newoldsr$mva[labind]==1)
aind<-which(newoldsr$mva[labind]==0)
yhigh<-max(as.numeric(ti99[5])*1.1,max(newoldsr$a)*1.1)

plot(newoldsr$od[labind][aind],newoldsr$a[labind][aind], col= 1, pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,yhigh))
points(newoldsr$od[labind][mvaind],newoldsr$a[labind][mvaind], col= "green", pch = 19, 
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
labs<-c("SÚRO","VÚV")

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
if(nlab==length(colors_user)){colors<-colors_user}
if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}
colors<-c("black","blue")

ti90<-normtol.int(newoldh$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldh$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldh$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("H-3 Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

labind <- which(newoldh$lab==labs[1])

pngfile = paste("pitna_voda_rada_h3.png",sep="")
png(filename=pngfile,width = 1000, height = 450, units = "px")

opar <- par(no.readonly = TRUE)
par(mar = c(6, 5, 4, 10.5))

mvaind<-which(newoldh$mva[labind]==1)
aind<-which(newoldh$mva[labind]==0)
yhigh<-max(as.numeric(ti99[5])*1.1,max(newoldh$a)*1.1)

plot(newoldh$od[labind][aind],newoldh$a[labind][aind], col= 1, pch = 19, 
     xlab="Datum", ylab="Aktivita [Bq/L]", cex=1.5, cex.axis=1.5, cex.lab=1.5, ylim=c(0,yhigh))
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





