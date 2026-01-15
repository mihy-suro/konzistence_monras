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

data <- read_excel("./Polozky_PR/Lesní Plody 2023.xlsx", sheet=2, guess_max=21474836)

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
# Lesní plody Cs-137 - Filtr
#==============================================================================

# dìlicí body pro referenèní a aktuální data:
newdata = "2023-01-01 00:00:00 CET"
olddata = "2013-01-01 00:00:00 CET"

kom = 0         # komodita
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
setwd("../reports/ostatni/")

#==============================================================================
# Boxplot maso
#==============================================================================
yearcs <- as.numeric(format(newoldcs$od,'%Y'))
newoldmvacs<-newoldcs[which(newoldcs$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(oldcs$a,newcs$a)
statscs<-paste("Lesní plody: Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4)) 

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("lesni_plody_cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 1000, units = "px")

par(mfrow=c(2,1), mai = c(1, 1, 1, 0.1))

# Cs-137 boxplot
if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(newoldcs$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/kg]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
mtext(statscs, side=3, line=0, cex=2)

# scatterplot

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newoldcs$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Lesní plody:  Prùmìr = ", signif(mean(newoldcs$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
outliers<-which(newoldcs$a>as.numeric(ti99[5]))
outind<-c(1:length(outliers))
outlabels<-paste(outind, " ... " ,newoldcs$kom[outliers],"/",newoldcs$om[outliers])

yhigh = max(as.numeric(ti99[5])*1.1,newoldcs$a*1.1)

plot(newoldcs$od,newoldcs$a, col= colors[1], pch = 19, cex=2, cex.lab=2, cex.axis=2, xlab="Datum", ylab="Aktivita [Bq/kg]")
points(newoldmvacs$od,newoldmvacs$a, col= "green", pch = 19, cex=2)
points(newoldcs$od[outliers],newoldcs$a[outliers], col= "red", pch = 19, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)

# leftalign<-newoldcs$od[length(newoldcs$od)-800]
# for(i in 1:length(outliers)){
#   text(newoldcs$od[outliers[i]],newoldcs$a[outliers[i]]+0.25,outind[i])  
#   text(leftalign,4.9-0.3*i,outlabels[i], pos = 4)  
# }

dev.off()


