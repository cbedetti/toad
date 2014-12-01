from generic.generictask import GenericTask
from modules import util
import glob
import os

__author__ = 'desmat'


class Parcellation(GenericTask):


    def __init__(self, subject):
        GenericTask.__init__(self, subject, 'preparation')
        self.id = subject.getConfig().get('parcellation', 'id')


    def implement(self):

        images = {'parcellation':self.getImage(self.dependDir,'aparc_aseg'),
                  'anatomical':self.getImage(self.dependDir,'anat_freesurfer'),
                  'brodmann':self.getImage(self.dependDir,'brodmann')}

        for key, value in images.iteritems():
            if value:
                self.info("Found {} area image, create link from {} to {}".format(key, value, self.workingDir))
                util.symlink(value, self.workingDir)

        if not (images['parcellation'] and images['anatomical'] and images['brodmann']):

            self.info("Set SUBJECTS_DIR to {}".format(self.workingDir))
            os.environ["SUBJECTS_DIR"] = self.workingDir

            anat = self.getImage(self.dependDir, 'anat')
            self.__reconAll(anat)
            self.__createBrodmannArea()

            #@TODO refactor this block of code
            if not images['anatomical']:
                anatMgzFreesurfers = glob.glob("{}/{}/mri/T1.mgz".format(self.workingDir, self.id))
                for anatMgzFreesurfer in anatMgzFreesurfers:
                    outputFile = os.path.join(self.workingDir,self.get('anat_freesurfer'))
                    self.__mgz2nii(anatMgzFreesurfer, outputFile)

            if not images['parcellation']:
                aparcMgzAsegs = glob.glob("{}/{}/mri/aparc+aseg.mgz".format(self.workingDir, self.id))
                for aparcMgzAseg in aparcMgzAsegs:
                    outputFile = os.path.join(self.workingDir, self.get('aparc_aseg'))
                    self.__mgz2nii(aparcMgzAseg, outputFile)

            if not images['brodmann']:
                brodmanns = glob.glob("{}/{}/mri/brodmann.mgz".format(self.workingDir, self.id))
                for brodmann in brodmanns:
                    outputFile = os.path.join(self.workingDir, self.get('brodmann'))
                    self.__mgz2nii(brodmann, outputFile)


    def __reconAll(self, source):
        """Performs all, or any part of, the FreeSurfer cortical reconstruction

        Args:
            source: The input source file

        """
        self.info("Starting parcellation with freesurfer")

        cmd = "recon-all -{} -i {} -subjid {} -sd {} -openmp {}"\
            .format(self.get('directive'), source, self.id, self.workingDir, self.getNTreads())
        self.info("Logging into {}/{}/scripts/recon-all.log".format(self.workingDir, self.id))
        self.launchCommand(cmd, 'log', 'log')

    def __createBrodmannArea(self):
        """create a Brodmann Area image

        """
        toadLabelsDir = os.path.join(self.toadDir, self.config.get("parcellation", "labels_dir"))
        labels = glob.glob("{}/*.label".format(toadLabelsDir))

        rhAnnotLabels =""
        lhAnnotLabels =""
        for labelDir in labels:
            label = os.path.basename(labelDir)
            hemisphere = label.split(".")[0]
            if hemisphere == "rh":
                rhAnnotLabels += "--l {}/{}/label/{} ".format(self.workingDir, self.id,label)
            if hemisphere == "lh":
                lhAnnotLabels += "--l {}/{}/label/{} ".format(self.workingDir, self.id,label)

            cmd = "mri_label2label --srcsubject fsaverage --srclabel {} " \
                "--trgsubject {} --trglabel {} --hemi {} --regmethod surface"\
                .format(labelDir, self.id, label, hemisphere)
            self.launchCommand(cmd, 'log')

        annotation = self.get('annotation')
        cmd = "mris_label2annot --s {} --h rh --ctab $FREESURFER_HOME/FreeSurferColorLUT.txt --a {} {}"\
            .format(self.id, annotation, rhAnnotLabels)
        self.launchCommand(cmd, 'log')

        cmd = "mris_label2annot --s {} --h lh --ctab $FREESURFER_HOME/FreeSurferColorLUT.txt --a {} {}"\
            .format(self.id, annotation, lhAnnotLabels)
        self.launchCommand(cmd, 'log')

        cmd = "mri_aparc2aseg --s {} --annot {} --o {}/{}/mri/{}"\
            .format(self.id, annotation, self.workingDir, self.id, self.get('brodmann_mgz'))
        self.launchCommand(cmd, 'log')


    def __mgz2nii(self, source, target, inType='mgz', outType='nii'):
        """Utility for converting between different file formats

        Args:
            source: The input source file
            target: The name of the resulting output file name
            inType: The image format of the original file. Default: mgz
            outType: The format of the resulting output image. Default: nii

        """
        self.info("convert {} image to {} ".format(source, target))
        cmd = "mri_convert -it {} -ot {} {} {}".format(inType, outType, source, target)
        util.launchCommand(cmd)


    def __cleanupReconAll(self):
        """Utility method that delete some symbolic links that are not usefull

        """
        self.info("Cleaning up extra files")
        for source in ["rh.EC_average", "lh.EC_average", "fsaverage", "segment.dat"]:
            self.info("Removing symbolic link {}".format(os.path.join(self.workingDir, source)))
            os.unlink(os.path.join(self.workingDir,source))


    def meetRequirement(self):

        images = {'high resolution': self.getImage(self.dependDir, 'anat')}
        return self.isAllImagesExists(images)


    def isDirty(self):

        images = {'parcellation': self.getImage(self.workingDir,'aparc_aseg'),
                  'anatomical': self.getImage(self.workingDir,'anat_freesurfer'),
                  'brodmann': self.getImage(self.workingDir,'brodmann')}

        return self.isSomeImagesMissing(images)


