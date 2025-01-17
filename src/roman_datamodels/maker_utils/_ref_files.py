import warnings

import asdf
import numpy as np
from astropy import units as u
from astropy.modeling import models

from roman_datamodels import stnode

from ._base import MESSAGE
from ._common_meta import (
    mk_ref_common,
    mk_ref_dark_meta,
    mk_ref_distoriton_meta,
    mk_ref_pixelarea_meta,
    mk_ref_readnoise_meta,
    mk_ref_units_dn_meta,
)

__all__ = [
    "mk_flat",
    "mk_dark",
    "mk_distortion",
    "mk_gain",
    "mk_ipc",
    "mk_linearity",
    "mk_inverse_linearity",
    "mk_mask",
    "mk_pixelarea",
    "mk_wfi_img_photom",
    "mk_readnoise",
    "mk_saturation",
    "mk_superbias",
    "mk_refpix",
]


def mk_flat(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Flat instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.FlatRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    flatref = stnode.FlatRef()
    flatref["meta"] = mk_ref_common("FLAT", **kwargs.get("meta", {}))

    flatref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))
    flatref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    flatref["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": flatref}
        af.write_to(filepath)
    else:
        return flatref


def mk_dark(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Dark Current instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DarkRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)")

    darkref = stnode.DarkRef()
    darkref["meta"] = mk_ref_dark_meta(**kwargs.get("meta", {}))

    darkref["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32))
    darkref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    darkref["err"] = kwargs.get("err", u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": darkref}
        af.write_to(filepath)
    else:
        return darkref


def mk_distortion(*, filepath=None, **kwargs):
    """
    Create a dummy Distortion instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.DistortionRef
    """
    distortionref = stnode.DistortionRef()
    distortionref["meta"] = mk_ref_distoriton_meta(**kwargs.get("meta", {}))

    distortionref["coordinate_distortion_transform"] = kwargs.get(
        "coordinate_distortion_transform", models.Shift(1) & models.Shift(2)
    )

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": distortionref}
        af.write_to(filepath)
    else:
        return distortionref


def mk_gain(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Gain instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.GainRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    gainref = stnode.GainRef()
    gainref["meta"] = mk_ref_common("GAIN", **kwargs.get("meta", {}))

    gainref["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.electron / u.DN, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": gainref}
        af.write_to(filepath)
    else:
        return gainref


def mk_ipc(*, shape=(3, 3), filepath=None, **kwargs):
    """
    Create a dummy IPC instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of array in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.IpcRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    ipcref = stnode.IpcRef()
    ipcref["meta"] = mk_ref_common("IPC", **kwargs.get("meta", {}))

    if "data" in kwargs:
        ipcref["data"] = kwargs["data"]
    else:
        ipcref["data"] = np.zeros(shape, dtype=np.float32)
        ipcref["data"][int(np.floor(shape[0] / 2))][int(np.floor(shape[1] / 2))] = 1.0

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": ipcref}
        af.write_to(filepath)
    else:
        return ipcref


def mk_linearity(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Linearity instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.LinearityRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)")

    linearityref = stnode.LinearityRef()
    linearityref["meta"] = mk_ref_units_dn_meta("LINEARITY", **kwargs.get("meta", {}))

    linearityref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    linearityref["coeffs"] = kwargs.get("coeffs", np.zeros(shape, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": linearityref}
        af.write_to(filepath)
    else:
        return linearityref


def mk_inverse_linearity(*, shape=(2, 4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy InverseLinearity instance (or file) with arrays and valid
    values for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.InverseLinearityRef
    """
    if len(shape) != 3:
        shape = (2, 4096, 4096)
        warnings.warn("Input shape must be 3D. Defaulting to (2, 4096, 4096)")

    inverselinearityref = stnode.InverseLinearityRef()
    inverselinearityref["meta"] = mk_ref_units_dn_meta("INVERSELINEARITY", **kwargs.get("meta", {}))

    inverselinearityref["dq"] = kwargs.get("dq", np.zeros(shape[1:], dtype=np.uint32))
    inverselinearityref["coeffs"] = kwargs.get("coeffs", np.zeros(shape, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": inverselinearityref}
        af.write_to(filepath)
    else:
        return inverselinearityref


def mk_mask(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Mask instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.MaskRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    maskref = stnode.MaskRef()
    maskref["meta"] = mk_ref_common("MASK", **kwargs.get("meta", {}))

    maskref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": maskref}
        af.write_to(filepath)
    else:
        return maskref


def mk_pixelarea(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Pixelarea instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.PixelareaRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    pixelarearef = stnode.PixelareaRef()
    pixelarearef["meta"] = mk_ref_pixelarea_meta(**kwargs.get("meta", {}))

    pixelarearef["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": pixelarearef}
        af.write_to(filepath)
    else:
        return pixelarearef


def _mk_phot_table_entry(key, **kwargs):
    """
    Create single phot_table entry for a given key.
    """
    if key in ("GRISM", "PRISM", "DARK"):
        entry = {
            "photmjsr": kwargs.get("photmjsr"),
            "uncertainty": kwargs.get("uncertainty"),
        }
    else:
        entry = {
            "photmjsr": kwargs.get("photmjsr", 1.0e-15 * np.random.random() * u.megajansky / u.steradian),
            "uncertainty": kwargs.get("uncertainty", 1.0e-16 * np.random.random() * u.megajansky / u.steradian),
        }

    entry["pixelareasr"] = kwargs.get("pixelareasr", 1.0e-13 * u.steradian)

    return entry


def _mk_phot_table(**kwargs):
    """
    Create the phot_table for the photom reference file.
    """
    entries = ("F062", "F087", "F106", "F129", "F146", "F158", "F184", "F213", "GRISM", "PRISM", "DARK")

    return {entry: _mk_phot_table_entry(entry, **kwargs.get(entry, {})) for entry in entries}


def mk_wfi_img_photom(*, filepath=None, **kwargs):
    """
    Create a dummy WFI Img Photom instance (or file) with dictionary and valid
    values for attributes required by the schema.

    Parameters
    ----------
    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.WfiImgPhotomRef
    """
    wfi_img_photomref = stnode.WfiImgPhotomRef()
    wfi_img_photomref["meta"] = mk_ref_common("PHOTOM", **kwargs.get("meta", {}))

    wfi_img_photomref["phot_table"] = _mk_phot_table(**kwargs.get("phot_table", {}))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": wfi_img_photomref}
        af.write_to(filepath)
    else:
        return wfi_img_photomref


def mk_readnoise(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Readnoise instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.ReadnoiseRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    readnoiseref = stnode.ReadnoiseRef()
    readnoiseref["meta"] = mk_ref_readnoise_meta(**kwargs.get("meta", {}))

    readnoiseref["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": readnoiseref}
        af.write_to(filepath)
    else:
        return readnoiseref


def mk_saturation(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Saturation instance (or file) with arrays and valid values
    for attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SaturationRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    saturationref = stnode.SaturationRef()
    saturationref["meta"] = mk_ref_common("SATURATION", **kwargs.get("meta", {}))

    saturationref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    saturationref["data"] = kwargs.get("data", u.Quantity(np.zeros(shape, dtype=np.float32), u.DN, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": saturationref}
        af.write_to(filepath)
    else:
        return saturationref


def mk_superbias(*, shape=(4096, 4096), filepath=None, **kwargs):
    """
    Create a dummy Superbias instance (or file) with arrays and valid values for
    attributes required by the schema.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.SuperbiasRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    superbiasref = stnode.SuperbiasRef()
    superbiasref["meta"] = mk_ref_common("BIAS", **kwargs.get("meta", {}))

    superbiasref["data"] = kwargs.get("data", np.zeros(shape, dtype=np.float32))
    superbiasref["dq"] = kwargs.get("dq", np.zeros(shape, dtype=np.uint32))
    superbiasref["err"] = kwargs.get("err", np.zeros(shape, dtype=np.float32))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": superbiasref}
        af.write_to(filepath)
    else:
        return superbiasref


def mk_refpix(*, shape=(32, 286721), filepath=None, **kwargs):
    """
    Create a dummy Refpix instance (or file) with arrays and valid values for
    attributes required by the schema.

    Note the default shape is intrinically connected to the FFT combined with
    specifics of the detector:
        - 32: is the number of detector channels (amp33 is a non-observation
            channel).
        - 286721 is more complex:
            There are 128 columns of the detector per channel, and for time read
            alignment purposes, these columns are padded by 12 additional
            columns. That is 140 columns per row. There are 4096 rows per
            channel. Each channel is then flattened into a 1D array of
            140 * 4096 = 573440 elements. Since the length is even the FFT of
            this array will be of length (573440 / 2) + 1 = 286721.
    Also, note the FFT gives a complex value and we are carrying full numerical
    precision which means it is a complex128.

    Parameters
    ----------
    shape
        (optional, keyword-only) Shape of arrays in the model.
        If shape is greater than 2D, the first two dimensions are used.

    filepath
        (optional, keyword-only) File name and path to write model to.

    Returns
    -------
    roman_datamodels.stnode.RefPixRef
    """
    if len(shape) > 2:
        shape = shape[:2]

        warnings.warn(f"{MESSAGE} assuming the first two entries. The remaining is thrown out!", UserWarning)

    refpix = stnode.RefpixRef()
    refpix["meta"] = mk_ref_units_dn_meta("REFPIX", **kwargs.get("meta", {}))

    refpix["gamma"] = kwargs.get("gamma", np.zeros(shape, dtype=np.complex128))
    refpix["zeta"] = kwargs.get("zeta", np.zeros(shape, dtype=np.complex128))
    refpix["alpha"] = kwargs.get("alpha", np.zeros(shape, dtype=np.complex128))

    if filepath:
        af = asdf.AsdfFile()
        af.tree = {"roman": refpix}
        af.write_to(filepath)
    else:
        return refpix
