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

data <- read_excel("./Polozky_ZP/Voda podzemní užitková 2023.xlsx", sheet=2, guess_max=21474836)

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
# Podzemni voda Cs-137 - Filtr
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

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("Podzemní užitková voda: Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# Cs-137 boxplot
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

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda Cs-137:  Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

outliers<-which(newoldcs$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldcs$kom[outliers],"/",newoldcs$om[outliers])

yhigh<-max(max(newoldcs$a)*1.1,as.numeric(ti95[5])*1.1)
plot(newoldcs$od,newoldcs$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvacs$od,newoldmvacs$a, col= jittercolmva, pch = 19, cex=2)
points(newoldcs$od[outliers],newoldcs$a[outliers], col= "red", pch = 19, cex=1.5)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

# leftalign<-newoldcs$od[length(newoldcs$od)-150]
# for(i in 1:length(outliers)){
#   text(newoldcs$od[outliers[i]],newoldcs$a[outliers[i]]+0.25,outind[i])  
#   text(leftalign,15-0.6*i,outlabels[i], pos = 4)  
# }

dev.off()


#==============================================================================
# Podzemni voda H3 - Filtr EDU
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  "EDU"        # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "H 3"       # radionuklid
allh<-ff(tmpdf,kom, om, lab, rn, start, end)
newh<-allh[which(allh$od>newdata),]
oldh<-allh[which((allh$od<=newdata)&(allh$od>olddata)),]
newoldh<-allh[which(allh$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldh[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))
ksh <- ks.test(oldh$a,newh$a)
statsh<-paste("Podz. už. voda EDU: H-3 D-statistika = ",signif(as.numeric(ksh[1]),4),";  p-hodnota = ",signif(as.numeric(ksh[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_h3_EDU.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# h-3 boxplot
if(ksh$p.value<=0.05){colnew<-"red"}
if(ksh$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearh))-1),colnew)

aind<-which(newoldh$mva==0)
boxplot(newoldh$a ~ yearh, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldh$a[aind] ~ yearh[aind], vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 19, col = jittercol, cex=2)
# stripchart(newoldmvah$a ~ yearmvah, vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 19, col = jittercolmva,cex=2)
mtext(statsh, side=3, line=0, cex=2)

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldh$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldh$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldh$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda H-3 EDU:  Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

aind<-which(newoldh$mva==0)
outliers<-which(newoldh$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldh$kom[outliers],"/",newoldh$om[outliers])

yhigh<-max(max(newoldh$a)*1.1,as.numeric(ti95[5])*1.1)
plot(newoldh$od,newoldh$a, pch = 19, cex=1.5, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvah$od,newoldmvah$a, col= jittercolmva, pch = 19, cex=2)
points(newoldh$od[outliers],newoldh$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

leftalign<-(newoldh$od[1]-1.0E7)
text(leftalign,400,unique(newoldh[outliers,]$om)[1], pos = 4, col=2)
text(leftalign,300,unique(newoldh[outliers,]$om)[2], pos = 4, col=2)
text(leftalign,200,unique(newoldh[outliers,]$om)[3], pos = 4, col=2)


dev.off()


#==============================================================================
# Podzemni voda H3 - Filtr ETE
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  "ETE"        # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "H 3"       # radionuklid
allh<-ff(tmpdf,kom, om, lab, rn, start, end)
newh<-allh[which(allh$od>newdata),]
oldh<-allh[which((allh$od<=newdata)&(allh$od>olddata)),]
newoldh<-allh[which(allh$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldh[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))
ksh <- ks.test(oldh$a,newh$a)
statsh<-paste("Podz. už. voda ETE: H-3 D-statistika = ",signif(as.numeric(ksh[1]),4),";  p-hodnota = ",signif(as.numeric(ksh[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_h3_ETE.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# h-3 boxplot
if(ksh$p.value<=0.05){colnew<-"red"}
if(ksh$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearh))-1),colnew)

aind<-which(newoldh$mva==0)
boxplot(newoldh$a ~ yearh, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldh$a[aind] ~ yearh[aind], vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvah$a ~ yearmvah, vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statsh, side=3, line=0, cex=2)

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldh$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldh$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldh$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda H-3 ETE:  Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

outliers<-which(newoldh$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldh$kom[outliers],"/",newoldh$om[outliers])

yhigh<-max(max(newoldh$a)*1.1,as.numeric(ti95[5])*1.1)
plot(newoldh$od,newoldh$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvah$od,newoldmvah$a, col= jittercolmva, pch = 19, cex=2)
points(newoldh$od[outliers],newoldh$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)
leftalign<-(newoldh$od[1]+1E8)
text(leftalign,80,"vrt OTKA 53", pos = 4, col="red")

dev.off()




#==============================================================================
# Podzemni voda H3 - Filtr SURAO
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  "SÚRO"        # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "H 3"       # radionuklid
allh<-ff(tmpdf,kom, om, lab, rn, start, end)
newh<-allh[which(allh$od>newdata),]
oldh<-allh[which((allh$od<=newdata)&(allh$od>olddata)),]
newoldh<-allh[which(allh$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearh <- as.numeric(format(newoldh$od,'%Y'))
newoldmvah<-newoldh[which(newoldh$mva==1),]
yearmvah <- as.numeric(format(newoldmvah$od,'%Y'))
ksh <- ks.test(oldh$a,newh$a)
statsh<-paste("Podz. už. voda SURO: H-3 D-statistika = ",signif(as.numeric(ksh[1]),4),";  p-hodnota = ",signif(as.numeric(ksh[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_h3_SURO_boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 500, units = "px")

par(mfrow=c(1,1), mai = c(1, 1, 1, 0.5))

# h-3 boxplot
if(ksh$p.value<=0.05){colnew<-"red"}
if(ksh$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearh))-1),colnew)

aind<-which(newoldh$mva==0)
boxplot(newoldh$a ~ yearh, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldh$a[aind] ~ yearh[aind], vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvah$a ~ yearmvah, vertical = TRUE, data = newoldh, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statsh, side=3, line=0, cex=2)

dev.off()

# scatterplot
pngfile = paste("voda_podzemni_h3_SURO_scatterplot.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.5))

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldh$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldh$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldh$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda H-3 SURO:  Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

outliers<-which(newoldh$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldh$kom[outliers],"/",newoldh$om[outliers])

yhigh<-max(max(newoldh$a)*1.1,as.numeric(ti95[5])*1.1)
plot(newoldh$od,newoldh$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvah$od,newoldmvah$a, col= jittercolmva, pch = 19, cex=2)
points(newoldh$od[outliers],newoldh$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

leftalign<-(newoldh$od[1]-1.4E7)
for(i in 1:length(outliers)){
  text(newoldh$od[outliers[i]],newoldh$a[outliers[i]]+500,outind[i])
  text(leftalign,6000-500*i,outlabels[i], pos = 4)
}



# zoom
yhigh<-150
limits <- paste("Podz. už. voda H-3 SURO (zoom):  Prùmìr = ", signif(mean(newoldh$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

plot(newoldh$od,newoldh$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvah$od,newoldmvah$a, col= jittercolmva, pch = 19, cex=2)
points(newoldh$od[outliers],newoldh$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

dev.off()



newoldh[(length(newoldh$a)-20):length(newoldh$a),]



#==============================================================================
# Podzemni voda SumaB- Filtr
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "SumaB"       # radionuklid
allSumaB<-ff(tmpdf,kom, om, lab, rn, start, end)
newSumaB<-allSumaB[which(allSumaB$od>newdata),]
oldSumaB<-allSumaB[which((allSumaB$od<=newdata)&(allSumaB$od>olddata)),]
newoldSumaB<-allSumaB[which(allSumaB$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearSumaB <- as.numeric(format(newoldSumaB$od,'%Y'))
newoldmvaSumaB<-newoldSumaB[which(newoldSumaB$mva==1),]
yearmvaSumaB <- as.numeric(format(newoldmvaSumaB$od,'%Y'))
ksSumaB <- ks.test(oldSumaB$a,newSumaB$a)
statsSumaB<-paste("Podzemní užitková voda: SumaB D-statistika = ",signif(as.numeric(ksSumaB[1]),4),";  p-hodnota = ",signif(as.numeric(ksSumaB[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_SumaB.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# SumaB boxplot
if(ksSumaB$p.value<=0.05){colnew<-"red"}
if(ksSumaB$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearSumaB))-1),colnew)

aind<-which(newoldSumaB$mva==0)
boxplot(newoldSumaB$a ~ yearSumaB, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldSumaB$a[aind] ~ yearSumaB[aind], vertical = TRUE, data = newoldSumaB, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvaSumaB$a ~ yearmvaSumaB, vertical = TRUE, data = newoldSumaB, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statsSumaB, side=3, line=0, cex=2)

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldSumaB$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldSumaB$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldSumaB$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda  SumaB:  Prùmìr = ", signif(mean(newoldSumaB$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

outliers<-which(newoldSumaB$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldSumaB$kom[outliers],"/",newoldSumaB$om[outliers])

yhigh<-max(max(newoldSumaB$a)*1.1,as.numeric(ti99[5])*1.1)
plot(newoldSumaB$od,newoldSumaB$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvaSumaB$od,newoldmvaSumaB$a, col= jittercolmva, pch = 19, cex=2)
points(newoldSumaB$od[outliers],newoldSumaB$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

leftalign<-(newoldSumaB$od[1]+1.5E7)
for(i in 1:length(outliers)){
  text(newoldSumaB$od[outliers[i]],newoldSumaB$a[outliers[i]]+0.1,outind[i])
  text(leftalign,2-0.1*i,outlabels[i], pos = 4)
}

dev.off()




#==============================================================================
# Podzemni voda SumaA- Filtr
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0             # komodita
om = 0              # odbìrové místo
lab =  0            # dodavatel dat
start = 0           # èasový výbìr od
end = 0             # èasový výbìr do

rn = "SumaA"       # radionuklid
allSumaA<-ff(tmpdf,kom, om, lab, rn, start, end)
newSumaA<-allSumaA[which(allSumaA$od>newdata),]
oldSumaA<-allSumaA[which((allSumaA$od<=newdata)&(allSumaA$od>olddata)),]
newoldSumaA<-allSumaA[which(allSumaA$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/podzemni_voda/")

#==============================================================================
# Boxplot podzemni voda
#==============================================================================
yearSumaA <- as.numeric(format(newoldSumaA$od,'%Y'))
newoldmvaSumaA<-newoldSumaA[which(newoldSumaA$mva==1),]
yearmvaSumaA <- as.numeric(format(newoldmvaSumaA$od,'%Y'))
ksSumaA <- ks.test(oldSumaA$a,newSumaA$a)
statsSumaA<-paste("Podzemní užitková voda: SumaA D-statistika = ",signif(as.numeric(ksSumaA[1]),4),";  p-hodnota = ",signif(as.numeric(ksSumaA[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("voda_podzemni_SumaA.png",sep="")
png(filename=pngfile,width = 1100, height = 1500, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# SumaA boxplot
if(ksSumaA$p.value<=0.05){colnew<-"red"}
if(ksSumaA$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearSumaA))-1),colnew)

aind<-which(newoldSumaA$mva==0)
boxplot(newoldSumaA$a ~ yearSumaA, outline = FALSE,ylab="aktivita [Bq/l]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
# stripchart(newoldSumaA$a[aind] ~ yearSumaA[aind], vertical = TRUE, data = newoldSumaA, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
# stripchart(newoldmvaSumaA$a ~ yearmvaSumaA, vertical = TRUE, data = newoldSumaA, 
#            method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statsSumaA, side=3, line=0, cex=2)

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldSumaA$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldSumaA$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldSumaA$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Podz. už. voda  SumaA:  Prùmìr = ", signif(mean(newoldSumaA$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

outliers<-which(newoldSumaA$a>as.numeric(ti99[5]))
outliers<-outliers[which(outliers %in% aind)]
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldSumaA$kom[outliers],"/",newoldSumaA$om[outliers])

yhigh<-max(max(newoldSumaA$a)*1.1,as.numeric(ti99[5])*1.1)
plot(newoldSumaA$od,newoldSumaA$a, pch = 19, cex=2, xlab="Datum", ylab="Aktivita [Bq/l]", col = jittercol, 
     ylim=c(0,yhigh), cex.lab = 2, cex.axis=2)
points(newoldmvaSumaA$od,newoldmvaSumaA$a, col= jittercolmva, pch = 19, cex=2)
points(newoldSumaA$od[outliers],newoldSumaA$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

leftalign<-(newoldSumaA$od[1]-1.5E7)
for(i in 1:length(outliers)){
  text(newoldSumaA$od[outliers[i]],newoldSumaA$a[outliers[i]]+500,outind[i])
  text(leftalign,15000-500*i,outlabels[i], pos = 4)
}

dev.off()

