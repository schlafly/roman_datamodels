import warnings

import asdf
import numpy as np
from astropy import units as u

from roman_datamodels import stnode

from ._base import MESSAGE
from ._common_meta import mk_common_meta, mk_guidewindow_meta, mk_msos_stack_meta, mk_photometry_meta, mk_resample_meta
from ._tagged_nodes import mk_cal_logs


def mk_level1_science_raw(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy level 1 ScienceRaw instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) (z, y, x) Shape of data array. This includes a
        four-pixel border representing the reference pixels. Default is
            (8, 4096, 4096)
        (8 integrations, 4088 x 4088 represent the science pixels, with the
        additional being the border reference pixels).

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiScienceRaw
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)")

    wfi_science_raw = stnode.WfiScienceRaw()
    wfi_science_raw["meta"] = mk_common_meta(**kwargs.get("meta", {}))

    n_groups = shape[0]

    wfi_science_raw["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16))

    # add amp 33 ref pix
    wfi_science_raw["amp33"] = kwargs.get(
        "amp33", u.Quantity(np.zeros((n_groups, 4096, 128), dtype=np.uint16), u.DN, dtype=np.uint16)
    )

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_science_raw}
        af.write_to(filepath)
    else:
        return wfi_science_raw


def mk_level2_image(*, shape=(4088, 4088), n_groups=8, filepath=None, **kwargs):
    """
    Create a dummy level 2 Image instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (y, x) of data array in the model (and
        its corresponding dq/err arrays). This specified size does NOT include
        the four-pixel border of reference pixels - those are trimmed at level
        2.  This size, however, is used to construct the additional arrays that
        contain the original border reference pixels (i.e if shape = (10, 10),
        the border reference pixel arrays will have (y, x) dimensions (14, 4)
        and (4, 14)). Default is 4088 x 4088.
        If shape is a tuple of length 3, the first element is assumed to be the
        n_groups and will override any settings there.

    n_groups : int
        (optional, keyword-only) The level 2 file is flattened, but it contains
        arrays for the original reference pixels which remain 3D. n_groups
        specifies what the z dimension of these arrays should be. Defaults to 8.

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImage
    """
    if len(shape) > 2:
        shape = shape[1:3]
        n_groups = shape[0]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_groups followed by y, x. The remaining is thrown out!", UserWarning
        )

    wfi_image = stnode.WfiImage()
    wfi_image["meta"] = mk_photometry_meta(**kwargs.get("meta", {}))

    # add border reference pixel arrays
    wfi_image["border_ref_pix_left"] = kwargs.get(
        "border_ref_pix_left", u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    )
    wfi_image["border_ref_pix_right"] = kwargs.get(
        "border_ref_pix_right", u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    )
    wfi_image["border_ref_pix_top"] = kwargs.get(
        "border_ref_pix_top", u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    )
    wfi_image["border_ref_pix_bottom"] = kwargs.get(
        "border_ref_pix_bottom", u.Quantity(np.zeros((n_groups, shape[0] + 8, 4), dtype=np.float32), u.DN, dtype=np.float32)
    )

    # and their dq arrays
    wfi_image["dq_border_ref_pix_left"] = kwargs.get("dq_border_ref_pix_left", np.zeros((shape[0] + 8, 4), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_right"] = kwargs.get("dq_border_ref_pix_right", np.zeros((shape[0] + 8, 4), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_top"] = kwargs.get("dq_border_ref_pix_top", np.zeros((4, shape[1] + 8), dtype=np.uint32))
    wfi_image["dq_border_ref_pix_bottom"] = kwargs.get("dq_border_ref_pix_bottom", np.zeros((4, shape[1] + 8), dtype=np.uint32))

    # add amp 33 ref pixel array
    amp33_size = (n_groups, 4096, 128)
    wfi_image["amp33"] = kwargs.get("amp33", u.Quantity(np.zeros(amp33_size, dtype=np.uint16), u.DN, dtype=np.uint16))
    wfi_image["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32))
    wfi_image["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    wfi_image["err"] = kwargs.get("err", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32))

    wfi_image["var_poisson"] = kwargs.get(
        "var_poisson", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_image["var_rnoise"] = kwargs.get(
        "var_rnoise", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_image["var_flat"] = kwargs.get(
        "var_flat", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_image["cal_logs"] = mk_cal_logs(**kwargs)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_image}
        af.write_to(filepath)
    else:
        return wfi_image


def mk_level3_mosaic(*, shape=(4088, 4088), n_images=2, filepath=None, **kwargs):
    """
    Create a dummy level 3 Mosaic instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (y, x) of data array in the model (and
        its corresponding dq/err arrays). Default is 4088 x 4088.
        If shape is a tuple of length 3, the first element is assumed to be
        n_images and will override the n_images parameter.

    n_images : int
        Number of images used to create the level 3 image. Defaults to 2.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiMosaic
    """
    if len(shape) > 2:
        shape = shape[1:3]
        n_images = shape[0]

        warnings.warn(
            f"{MESSAGE} assuming the first entry is n_images followed by y, x. The remaining is thrown out!", UserWarning
        )

    wfi_mosaic = stnode.WfiMosaic()
    wfi_mosaic["meta"] = mk_resample_meta(**kwargs.get("meta", {}))

    wfi_mosaic["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32))
    wfi_mosaic["err"] = kwargs.get("err", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32))
    wfi_mosaic["context"] = kwargs.get("context", np.zeros((n_images,) + shape, dtype=np.uint32))
    wfi_mosaic["weight"] = kwargs.get("weight", np.zeros(shape, dtype=np.float32))

    wfi_mosaic["var_poisson"] = kwargs.get(
        "var_poisson", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_mosaic["var_rnoise"] = kwargs.get(
        "var_rnoise", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_mosaic["var_flat"] = kwargs.get(
        "var_flat", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    wfi_mosaic["cal_logs"] = mk_cal_logs(**kwargs)

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_mosaic}
        af.write_to(filepath)
    else:
        return wfi_mosaic


def mk_msos_stack(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Level 3 MSOS stack instance (or file) with arrays and valid values

    Parameters
    ----------
    shape : tuple, int
        (optional) Shape (z, y, x) of data array in the model (and its
        corresponding dq/err arrays). This specified size includes the
        four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

    filepath : str
        (optional) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MsosStack
    """
    if len(shape) > 2:
        shape = shape[1:3]

        warnings.warn(f"{MESSAGE} assuming the the first two entries are y, x. The remaining is thrown out!", UserWarning)

    msos_stack = stnode.MsosStack()
    msos_stack["meta"] = mk_msos_stack_meta(**kwargs.get("meta", {}))

    msos_stack["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float64))
    msos_stack["uncertainty"] = kwargs.get("uncertainty", np.zeros(shape, dtype=np.float64))
    msos_stack["mask"] = kwargs.get("mask", np.zeros(shape, dtype=np.uint8))
    msos_stack["coverage"] = kwargs.get("coverage", np.zeros(shape, dtype=np.uint8))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": msos_stack}
        af.write_to(filepath)
    else:
        return msos_stack


def mk_ramp(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Ramp instance (or file) with arrays and valid values for attributes
    required by the schema.

    Parameters
    ----------
    shape : tuple, int
        (optional, keyword-only) Shape (z, y, x) of data array in the model (and
        its corresponding dq/err arrays). This specified size includes the
        four-pixel border of reference pixels. Default is 8 x 4096 x 4096.

    filepath : str
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Ramp
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)")

    ramp = stnode.Ramp()
    ramp["meta"] = mk_common_meta(**kwargs.get("meta", {}))

    # add border reference pixel arrays
    ramp["border_ref_pix_left"] = kwargs.get(
        "border_ref_pix_left", u.Quantity(np.zeros((shape[0], shape[1], 4), dtype=np.float32), u.DN, dtype=np.float32)
    )
    ramp["border_ref_pix_right"] = kwargs.get(
        "border_ref_pix_right", u.Quantity(np.zeros((shape[0], shape[1], 4), dtype=np.float32), u.DN, dtype=np.float32)
    )
    ramp["border_ref_pix_top"] = kwargs.get(
        "border_ref_pix_top", u.Quantity(np.zeros((shape[0], 4, shape[2]), dtype=np.float32), u.DN, dtype=np.float32)
    )
    ramp["border_ref_pix_bottom"] = kwargs.get(
        "border_ref_pix_bottom", u.Quantity(np.zeros((shape[0], 4, shape[2]), dtype=np.float32), u.DN, dtype=np.float32)
    )

    # and their dq arrays
    ramp["dq_border_ref_pix_left"] = kwargs.get("dq_border_ref_pix_left", np.zeros((shape[1], 4), dtype=np.uint32))
    ramp["dq_border_ref_pix_right"] = kwargs.get("dq_border_ref_pix_right", np.zeros((shape[1], 4), dtype=np.uint32))
    ramp["dq_border_ref_pix_top"] = kwargs.get("dq_border_ref_pix_top", np.zeros((4, shape[2]), dtype=np.uint32))
    ramp["dq_border_ref_pix_bottom"] = kwargs.get("dq_border_ref_pix_bottom", np.zeros((4, shape[2]), dtype=np.uint32))

    # add amp 33 ref pixel array
    ramp["amp33"] = kwargs.get("amp33", u.Quantity(np.zeros((shape[0], shape[1], 128), dtype=np.uint16), u.DN, dtype=np.uint16))

    ramp["data"] = kwargs.get("data", u.Quantity(np.full(shape, 1.0, dtype=np.float32), u.DN, dtype=np.float32))
    ramp["pixeldq"] = kwargs.get("pixeldq", np.zeros(shape[1:], dtype=np.uint32))
    ramp["groupdq"] = kwargs.get("groupdq", np.zeros(shape, dtype=np.uint8))
    ramp["err"] = kwargs.get("err", u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": ramp}
        af.write_to(filepath)
    else:
        return ramp


def mk_ramp_fit_output(*, shape=(8, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Rampfit Output instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RampFitOutput
    """
    if len(shape) != 3:
        shape = (8, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (8, 4096, 4096)")

    rampfitoutput = stnode.RampFitOutput()
    rampfitoutput["meta"] = mk_common_meta(**kwargs.get("meta", {}))

    rampfitoutput["slope"] = kwargs.get(
        "slope", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    )
    rampfitoutput["sigslope"] = kwargs.get(
        "sigslope", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.s, dtype=np.float32)
    )
    rampfitoutput["yint"] = kwargs.get("yint", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32))
    rampfitoutput["sigyint"] = kwargs.get("sigyint", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32))
    rampfitoutput["pedestal"] = kwargs.get(
        "pedestal", u.Quantity(np.zeros(shape[1:], dtype=np.float32), u.electron, dtype=np.float32)
    )
    rampfitoutput["weights"] = kwargs.get("weights", np.zeros(shape, dtype=np.float32))
    rampfitoutput["crmag"] = kwargs.get("crmag", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron, dtype=np.float32))
    rampfitoutput["var_poisson"] = kwargs.get(
        "var_poisson", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )
    rampfitoutput["var_rnoise"] = kwargs.get(
        "var_rnoise", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron**2 / u.s**2, dtype=np.float32)
    )

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": rampfitoutput}
        af.write_to(filepath)
    else:
        return rampfitoutput


def mk_rampfitoutput(**kwargs):
    warnings.warn("mk_rampfitoutput is deprecated. Use mk_rampfit_output instead.", DeprecationWarning)

    return mk_ramp_fit_output(**kwargs)


def mk_associations(*, shape=(2, 3, 1), filepath=None, **kwargs):
    """
    Create a dummy Association table instance (or file) with table and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape : tuple
        (optional, keyword-only) The shape of the member elements of products.
    filepath : string
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.AssociationsModel
    """

    associations = stnode.Associations()

    associations["asn_type"] = kwargs.get("asn_type", "image")
    associations["asn_rule"] = kwargs.get("asn_rule", "candidate_Asn_Lv2Image_i2d")
    associations["version_id"] = kwargs.get("version_id", "null")
    associations["code_version"] = kwargs.get("code_version", "0.16.2.dev16+g640b0b79")
    associations["degraded_status"] = kwargs.get("degraded_status", "No known degraded exposures in association.")
    associations["program"] = kwargs.get("program", 1)
    associations["constraints"] = kwargs.get(
        "constraints",
        (
            "DMSAttrConstraint({'name': 'program', 'sources': ['program'], "
            "'value': '001'})\nConstraint_TargetAcq({'name': 'target_acq', 'value': "
            "'target_acquisition'})\nDMSAttrConstraint({'name': 'science', "
            "'DMSAttrConstraint({'name': 'asn_candidate','sources': "
            "['asn_candidate'], 'value': \"\\\\('o036',\\\\ 'observation'\\\\)\"})"
        ),
    )
    associations["asn_id"] = kwargs.get("asn_id", "o036")
    associations["asn_pool"] = kwargs.get("asn_pool", "r00001_20200530t023154_pool")
    associations["target"] = kwargs.get("target", 16)

    file_idx = 0
    if "products" in kwargs:
        associations["products"] = kwargs["products"]
    else:
        associations["products"] = []
        CHOICES = ["SCIENCE", "CALIBRATION", "ENGINEERING"]
        for product_idx, members in enumerate(shape):
            members_lst = []
            for member_idx in range(members):
                members_lst.append(
                    {"expname": "file_" + str(file_idx) + ".asdf", "exposerr": "null", "exptype": CHOICES[member_idx % 3]}
                )
                file_idx += 1
            associations["products"].append({"name": f"product{product_idx}", "members": members_lst})

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": associations}
        af.write_to(filepath)
    else:
        return associations


def mk_guidewindow(*, shape=(2, 8, 16, 32, 32), filepath=None, **kwargs):
    """
    Create a dummy Guidewindow instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.Guidewindow
    """
    if len(shape) != 5:
        shape = (2, 8, 16, 32, 32)
        warnings.warn("Input shape must be 5D. Defaulting to (2, 8, 16, 32, 32)")

    guidewindow = stnode.Guidewindow()
    guidewindow["meta"] = mk_guidewindow_meta(**kwargs.get("meta", {}))

    guidewindow["pedestal_frames"] = kwargs.get(
        "pedestal_frames", u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)
    )
    guidewindow["signal_frames"] = kwargs.get(
        "signal_frames", u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16)
    )
    guidewindow["amp33"] = kwargs.get("amp33", u.Quantity(np.zeros(shape, dtype=np.uint16), u.DN, dtype=np.uint16))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": guidewindow}
        af.write_to(filepath)
    else:
        return guidewindow
