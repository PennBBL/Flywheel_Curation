'''
This heuristic curates most of the PNC LG project. The heuristic
ignores the following (taken from fwheudiconv output):

Series not recognized!:  localizer localizer
Series not recognized!:  epi_singlerep_advshim epi_singlerep_advshim
Series not recognized!:  MPRAGE_TI1110_ipat2_moco3 MPRAGE_NAVprotocol
Series not recognized!:  T2star T2star
Series not recognized!:  localizer_32channel localizer_32channel
Series not recognized!:  Axial_T2_star_v2 Axial_T2_star_v2
Series not recognized!:  epi_singlerep_advshim epi_singlerep_advshim
Series not recognized!:  Axial_T2_star Axial_T2_star
Series not recognized!:  MPRAGE_NAVprotocol MPRAGE_NAVprotocol
'''

import os


def create_key(template, outtype=('nii.gz',), annotation_classes=None):
    if template is None or not template:
        raise ValueError('Template must be a valid format string')
    return template, outtype, annotation_classes


# Create Keys
t1w = create_key(
   'sub-{subject}/{session}/anat/sub-{subject}_{session}_T1w')
t2w = create_key(
   'sub-{subject}/{session}/anat/sub-{subject}_{session}_T2w')
# t2star = create_key(
#   'sub-{subject}/{session}/anat/sub-{subject}_{session}_T2star')

# Field maps
b0_mag_single_phasediff = create_key(
   'sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude{item}')
b0_phase_single = create_key(
   'sub-{subject}/{session}/fmap/sub-{subject}_{session}_phasediff')
b0_mag_multi_phasediff = create_key(
   'sub-{subject}/{session}/fmap/sub-{subject}_{session}_magnitude{item}')
b0_phase_multi = create_key(
   'sub-{subject}/{session}/fmap/sub-{subject}_{session}_phase{item}')


# fmri scans
rest_bold_100 = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_acq-100_bold')
rest_bold_124 = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold')
rest_bold_204 = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold')
dwi_run1 = create_key(
    'sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-01_dwi')
dwi_run2 = create_key(
    'sub-{subject}/{session}/dwi/sub-{subject}_{session}_run-02_dwi')
frac2back = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-frac2back')
demo = create_key(
    'sub-{subject}/{session}/func/sub-{subject}_{session}_task-idemo')
#
## ASL scans
asl = create_key(
   'sub-{subject}/{session}/asl/sub-{subject}_{session}_asl')
#asl_dicomref = create_key(
#   'sub-{subject}/{session}/asl/sub-{subject}_{session}_acq-ref_asl')
m0 = create_key(
   'sub-{subject}/{session}/asl/sub-{subject}_{session}_m0')
#mean_perf = create_key(
#   'sub-{subject}/{session}/asl/sub-{subject}_{session}_mean-perfusion')


def infotodict(seqinfo):
    """Heuristic evaluator for determining which runs belong where

    allowed template fields - follow python string module:

    item: index within category
    subject: participant id
    seqitem: run number during scanning
    subindex: sub index within group
    """

    last_run = len(seqinfo)

    info = {t1w: [], t2w: [],
            dwi_run1: [], dwi_run2: [],
            b0_mag_single_phasediff: [], b0_phase_single: [],
            b0_mag_multi_phasediff: [], b0_phase_multi: [],
            rest_bold_100: [], rest_bold_124: [], rest_bold_204: [],
            frac2back: [], demo: [], #t2star: [], pe_rev:[], rest_sb:[],
            # asl_dicomref:[], face:[], asl:[],
            m0: [], asl: []  # , mean_perf:[]
            }

    def get_latest_series(key, s):
        #    if len(info[key]) == 0:
        info[key].append(s.series_id)
    #    else:
    #        info[key] = [s.series_id]

    for s in seqinfo:
        protocol = s.protocol_name.lower()

        # anatomical
        if "mprage" in protocol and "nav" not in protocol and "MOSAIC" not in s.image_type and "DERIVED" not in s.image_type:
            get_latest_series(t1w, s)
        elif "t2_sag" in protocol:
            get_latest_series(t2w, s)

        # elif "t2" in protocol and "star" in protocol:
        #     get_latest_series(t2star, s)

        # Fieldmaps
        elif "b0map" in protocol and "M" in s.image_type:
            if "onesizefitsall" in s.series_description:
                info[b0_mag_multi_phasediff].append(s.series_id)
            else:
                info[b0_mag_single_phasediff].append(s.series_id)

        elif "b0map" in protocol and "P" in s.image_type:
            if "onesizefitsall" in s.series_description:
                info[b0_phase_multi].append(s.series_id)
            else:
                info[b0_phase_single].append(s.series_id)

#        elif "topup_ref" in protocol:
#            get_latest_series(pe_rev, s)
        elif "dti" in protocol and not s.is_derived:
            if "35" in protocol:
                get_latest_series(dwi_run1, s)
            elif "36" in protocol:
                get_latest_series(dwi_run2, s)

        elif "pcasl" in protocol:
            if s.series_description.endswith("_M0"):
                get_latest_series(m0, s)
            elif "MoCo" in s.series_description:
                get_latest_series(asl, s)

        elif "frac2back" in protocol:
            get_latest_series(frac2back, s)
        elif "idemo" in protocol:
            get_latest_series(demo, s)
#        elif "face" in protocol:
#            get_latest_series(face,s)
        elif "restbold" in protocol:
            if "100" in protocol:
                get_latest_series(rest_bold_100, s)
            elif "124" in protocol:
                get_latest_series(rest_bold_124, s)
            elif "204" in protocol:
                get_latest_series(rest_bold_204, s)

        else:
            print("Series not recognized!: ", s.protocol_name, s.series_description)
    return info

IntendedFor = {
    b0_mag_multi_phasediff: [
        '{session}/func/sub-{subject}_{session}_task-rest_acq-100_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-01_dwi.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-02_dwi.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-frac2back.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-idemo.nii.gz'
    ],

    b0_phase_multi: [
        '{session}/func/sub-{subject}_{session}_task-rest_acq-100_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-01_dwi.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-02_dwi.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-frac2back.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-idemo.nii.gz'
    ],

    b0_mag_single_phasediff: [
        '{session}/func/sub-{subject}_{session}_task-rest_acq-100_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-01_dwi.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-02_dwi.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-frac2back.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-idemo.nii.gz'
    ],

    b0_phase_single: [
        '{session}/func/sub-{subject}_{session}_task-rest_acq-100_bold.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-rest_acq-singleband_bold.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-01_dwi.nii.gz',
        '{session}/dwi/sub-{subject}_{session}_run-02_dwi.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-frac2back.nii.gz',
        '{session}/func/sub-{subject}_{session}_task-idemo.nii.gz'
    ]
}

def gather_session_indeces():
    # use flywheel to gather a dict of all session session_labels
    # with their corresponding index by time, within the subject
    # query subjects
    import flywheel
    fw = flywheel.Client()
    project_obj = fw.projects.find_first('label="{}"'.format("PNC_LG_810336"))
    subjects = project_obj.subjects()

    # initialise dict of correctly padded subject labels
    subs_dict = {x.label.zfill(6): [] for x in subjects}

    # for each correctly labeled subject, list their sessions
    for x in subjects:

        sess_list = x.sessions()
        subs_dict[x.label.zfill(6)].extend(sess_list)

    sess_dict = {}

    # loop over each subject's sessions, sort, and enumerate
    for k, v in subs_dict.items():

        v = sorted(v, key=lambda x: x.timestamp)

        for i, y in enumerate(v):
            sess_dict[y.label] = "PNC" + str(i + 2)

    # return to main namespace
    return sess_dict

sessions = gather_session_indeces()

def ReplaceSession(ses_label):

    return str(sessions[ses_label])
