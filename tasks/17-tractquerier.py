# -*- coding: utf-8 -*-
import os
import shutil
from core.toad.generictask import GenericTask
from lib import mriutil, util
from lib.images import Images


class Tractquerier(GenericTask):

    def __init__(self, subject):
        GenericTask.__init__(
            self, subject,
            'preparation', 'upsampling', 'registration', 'atlasregistration',
            'tractographymrtrix', 'qa')
        self.setCleanupBeforeImplement(False)


    def implement(self):
        shutil.copy(self.queries, self.workingDir)
        shutil.copy(self.tq_dict, self.workingDir)

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)  # Get number of directions

        self.tractographyTrk = self.__getTractography(nbDirections)  # Load tractography

        atlasResample = self.__getAtlas()  # Get atlas to refere to

        self.__tractQuerier(
                self.tractographyTrk, atlasResample,
                self.workingDir, self.queries)


    def __getTractography(self, nbDirections):
        if nbDirections <= 45 and not self.get('tractographymrtrix', 'forceHardi'):
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'
        return self.getTractographymrtrixImage('dwi', postfixTractography, 'trk')


    def __getAtlas(self):
        atlas = self.get('atlas')
        target = self.getAtlasRegistrationImage(atlas, 'resample')
        if not target:
            target = self.getRegistrationImage(atlas, 'resample')
        else:
            self.info("No atlas resample found in tractquerier task")
        return target


    def __tractQuerier(self, trk, atlas, qryDict, qryFile):
        target = self.buildName(trk, None, 'trk')
        cmd = "tract_querier -t {} -a {} -I {} -q {} -o {}"
        cmd = cmd.format(trk, atlas, qryDict, qryFile, target)
        self.launchCommand(cmd)
        return target


    def __buildNameTractQuerierOutputs(self):
        self.queries = [self.getImage('dwi', 'corpus_callosum', 'trk'),
                        self.getImage('dwi', 'cortico_spinal.left', 'trk'),
                        self.getImage('dwi', 'cortico_spinal.right', 'trk'),
                        self.getImage('dwi', 'inferior_fronto_occipital.left', 'trk'),
                        self.getImage('dwi', 'inferior_fronto_occipital.right', 'trk'),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.left', 'trk'),
                        self.getImage('dwi', 'inferior_longitudinal_fasciculus.right', 'trk'),
                        self.getImage('dwi', 'uncinate_fasciculus.left', 'trk'),
                        self.getImage('dwi', 'uncinate_fasciculus.right', 'trk')]


    def isIgnore(self):
        return self.get("ignore")


    def meetRequirement(self):
        """Validate if all requirements have been met prior to launch the task
        Returns:
            True if all requirement are meet, False otherwise
        """

        images = Images()

        dwi = self.getUpsamplingImage('dwi', 'upsample')
        nbDirections = mriutil.getNbDirectionsFromDWI(dwi)  # Get number of directions

        if nbDirections <= 45 and not self.get('tractographymrtrix', 'forceHardi'):
            postfixTractography = 'tensor_prob'
        else:
            postfixTractography = 'hardi_prob'

        Images((self.getTractographymrtrixImage('dwi', postfixTractography, 'trk'),'Tractography file'),
                (self.__getAtlas(),'Atlas'))  # Check if tractographies are available

        return images


    def isDirty(self):
        """Validate if this tasks need to be submit during the execution
        Returns:
            True if any expected file or resource is missing, False otherwise
        """
        trks = self.getImages('dwi', None, 'trk')

        if len(trks) > 0:
            return False
        else:
            return True


    def qaSupplier(self):
        """Create and supply images for the report generated by qa task

        """
        qaImages = Images()

        information = "Warning: due to storage restriction, streamlines were " \
                      "downsampled. Even if there is no difference in structural " \
                      "connectivity, you should be careful before computing any " \
                      "metrics along these streamlines.\n To run toad without this " \
                      "downsampling, please refer to the documentation."

        if self.defaultQuery:
            # get images
            norm = self.getRegistrationImage("norm", "resample")
            self.__buildNameTractQuerierOutputs()
            # images production
            tags = (
                (self.queries[0],
                 'Corpus Callosum',
                 95, 60, 40, -80, 0, 160),
                (self.queries[1],
                 'Corticospinal tract Left',
                 95, 80, 40, -90, 0, 160),
                (self.queries[2],
                 'Corticospinal tract right',
                 95, 80, 40, -90, 0, 200),
                (self.queries[3],
                 'Inferior Fronto Occipital tract left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[4],
                 'Inferior Fronto Occipital tract right',
                 95, 80, 40, -90, 0, -90),
                (self.queries[5],
                 'inferior Longitudinal Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[6],
                 'Inferior Longitudinal Fasciculus right',
                 95, 80, 40, -90, 0, -90),
                (self.queries[7],
                 'Uncinate Fasciculus left',
                 95, 80, 40, -90, 0, 90),
                (self.queries[8],
                 'Uncinate Fasciculus right',
                 95, 80, 40, -90, 0, -90))

            for data, description, xSlice, ySlice, zSlice, xRot, yRot, zRot in tags:
                if data is not None:
                    imageQa = self.plotTrk(data, norm, None, xSlice, ySlice, zSlice, xRot, yRot, zRot)
                    qaImages.append((imageQa, description))
        else:
            information = """
            Because you didn't choose default queries and dictionnary,
            we are not able to create proper screenshots of the output bundles.
            """
        qaImages.setInformation(information)

        return qaImages
