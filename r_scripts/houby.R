
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

data <- read_excel("./polozky_PR/Houby 2023.xlsx", sheet=2, guess_max=21474836)

kom_ID<-data$ID_Monit_položka_OM 
kom<-trimws(sapply(strsplit(data$Monitorovaná_položka_OM,"/"), tail, 1))
om<-data$Odbìrové_místo
om_ID<-data$ID_OM
lab<-data$Dodavatel_dat
a<-data$Hodnota_cista
u<-data$Nejistota
jed<-data$Jednotka
mva<-data$Pod_MVA
od<-as.POSIXct(data$Datum_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
do<-as.POSIXct(data$Konec_odberu_mistni_cas,format="%d.%m.%Y %H:%M",tz=Sys.timezone())
rn<-data$Nuklid
tmpdf<-data.frame(kom_ID,kom, om, om_ID, lab, a, u, mva, jed, od, do, rn, stringsAsFactors=FALSE)

#==============================================================================
# Nastavení filtru (0 = vše)
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

all<-ff(tmpdf,kom, om, lab, rn, start, end)
new<-all[which(all$od>newdata),]
old<-all[which((all$od<=newdata)&(all$od>olddata)),]
newold<-all[which(all$od>olddata),]

ScriptFolder<-dirname(rstudioapi::getSourceEditorContext()$path)
setwd(ScriptFolder)
setwd("../reports/houby/")

#==============================================================================
# Boxplot vuv + suro
#==============================================================================

yearcs <- as.numeric(format(newold$od,'%Y'))
newoldmvacs<-newold[which(newold$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(old$a,new$a)
statscs<-paste("Houby - Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4))

colnew="red"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("houby__boxplot.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

par(mfrow=c(1,1), mai = c(1, 1, 1, 0.1))

if(kscs$p.value<=0.05){colnew<-"red"}
if(kscs$p.value>0.05){colnew<-"green"}
colors = c(rep("grey",length(unique(yearcs))-1),colnew)

boxplot(newold$a ~ yearcs, outline = FALSE,ylab="aktivita [Bq/kg]",xlab="Datum", col=colors,
        boxlwd = 2,whisklwd=2,staplelwd=2, cex.lab = 2, cex.axis=2, cex=2)
stripchart(newold$a ~ yearcs, vertical = TRUE, data = newold, 
           method = "jitter", add = TRUE, pch = 20, col = jittercol, cex=2)
stripchart(newoldmvacs$a ~ yearmvacs, vertical = TRUE, data = newold, 
           method = "jitter", add = TRUE, pch = 20, col = jittercolmva,cex=2)
mtext(statscs, side=3, line=0, cex=2)

dev.off()

#==============================================================================
# GRAFY
#==============================================================================
# #==============================================================================
# # èasová øada s rozlišením laborek
# #==============================================================================
# title = "Houby"
# 
# group <- as.factor(newold$lab)
# labs<-levels(group)
# 
# labs_other <- labs[labs != "SVÚ" & labs != "SÚRO"]
# labs <- factor(group,levels = c("SVÚ","SÚRO",labs_other))
# labnames<-levels(labs)  
# nlab <- length(labnames)
# 
# colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
# if(nlab==length(colors_user)){colors<-colors_user}
# if(nlab>length(colors_user)){colors<-c(colors_user,distinctColorPalette(nlab-length(colors_user)))}
# if(nlab<length(colors_user)){colors<-colors_user[1:nlab]}
# 
# ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
# ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
# ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
# limits <- paste("Houby - Cs-137 Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")
# 
# labind <- which(newold$lab==labnames[1])
# 
 opar <- par(no.readonly = TRUE)
# par(mar = c(6, 5, 4, 12.5))
# plot(newold$od[labind],newold$a[labind], col= colors[1], pch = 19, xlab="Datum", ylab="Aktivita [Bq/kg]", main=title)
# 
# abline(h=ti90[5], col = "blue")
# abline(h=ti95[5],col = "orange")
# abline(h=ti99[5], col = "red")
# mtext(limits, side=3, line=0)
# 
# for (i in 2:nlab){
#   labind <-which(newold$lab==labnames[i])
#   points(newold$od[labind],newold$a[labind], col = colors[i], pch=19)
# }
# 
# 
# legend("topright",
#        inset = c(-0.31, 0), 
#        legend = labnames, 
#        col = colors,
#        pch = 19,
#        xpd = TRUE) 
# 
# on.exit(par(opar))

#==============================================================================
# lognormální qqplot s vyznaèenými aktuálními daty (necenzorovaná verze)
#==============================================================================
pngfile = paste("houby_qqplot_Cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

par(opar)
qq<-qqPlot(newold$a, distribution = "lnorm", param.list = list(mean = 0, sd = 1))
newold$typ<-"old"
newold$typ[which(newold$do>newdata)]<-"new"

dftyp <-data.frame(a=newold$a,typ=newold$typ)
dfsorted <- dftyp[order(dftyp$a),] 
indnew<-which(dfsorted$typ=="new")

plot(qq$x,qq$y, xlab="kvantily normálního rozdìlení", ylab="ln(aktivita)", pch=1)
points(qq$x[indnew],qq$y[indnew],col=rgb(red = 1, green = 0, blue = 0, alpha = 0.6), pch=0)
abline(mean(qq$y), sd(qq$y))
legend("topleft", legend=c("Referenèní data", "Aktuální data"), col=c("black", "red"), pch=c(1,0),cex=0.8)
mtext("Houby Cs-137", side=3, line=0, cex=2)
dev.off()




#==============================================================================
# scatterplot
#==============================================================================

yearcs <- as.numeric(format(newold$od,'%Y'))
newoldmvacs<-newold[which(newold$mva==1),]
yearmvacs <- as.numeric(format(newoldmvacs$od,'%Y'))
kscs <- ks.test(old$a,new$a)
statscs<-paste("Houby - Cs-137 D-statistika = ",signif(as.numeric(kscs[1]),4),";  p-hodnota = ",signif(as.numeric(kscs[2]),4)) 

colnew="black"
jittercol <- rgb(0, 0, 255, max = 255, alpha = 50, names = "blue50")
jittercolmva <- rgb(0, 255, 0, max = 255, alpha = 50)

###################################
pngfile = paste("houby_casrada_cs137.png",sep="")
png(filename=pngfile,width = 1100, height = 700, units = "px")

par(mfrow=c(1,1), mai = c(1, 1, 1, 0.1))

colors_user <- c(rgb(0,0,0,1/4),rgb(1,0,0,1/4),rgb(0,0,1,1/4))
ti90<-normtol.int(newold$a, alpha = 0.05, P = 0.90, side = 1, log.norm = TRUE)
ti95<-normtol.int(newold$a, alpha = 0.05, P = 0.95, side = 1, log.norm = TRUE)
ti99<-normtol.int(newold$a, alpha = 0.05, P = 0.99, side = 1, log.norm = TRUE)
limits <- paste("Houby - Cs-137  Prùmìr = ", signif(mean(newold$a),3),";  TI90 = ",signif(ti90[5],3),";  TI95 = ",signif(ti95[5],3), ";  TI99 = ",signif(ti99[5],3),sep="")

plot(newold$od,newold$a, col= colors(1), pch = 20, xaxp = c(2013, 2023, 5), cex=2, cex.lab = 2, cex.axis=2, xlab="Datum", ylab="Aktivita [Bq/kg]")
points(newoldmvacs$od,newoldmvacs$a, col= "green", pch = 19, cex=2)
points(newold$od,newold$a, col= "black", pch = 20, cex=2)
abline(h=ti90[5], col = "blue")
abline(h=ti95[5],col = "orange")
abline(h=ti99[5], col = "red")
mtext(limits, side=3, line=0, cex=2)


dev.off()

