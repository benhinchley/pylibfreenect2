# coding: utf-8

import numpy as np

from nose.tools import raises

from pylibfreenect2 import Freenect2, FrameMap, SyncMultiFrameListener
from pylibfreenect2 import FrameType, Registration, Frame


def test_sync_multi_frame():
    fn = Freenect2()

    num_devices = fn.enumerateDevices()
    assert num_devices > 0

    serial = fn.getDefaultDeviceSerialNumber()
    assert serial == fn.getDeviceSerialNumber(0)

    # TODO: 本当はどっちもテストしたい
    # device = fn.openDefaultDevice()
    device = fn.openDevice(serial)

    assert fn.getDefaultDeviceSerialNumber() == device.getSerialNumber()
    device.getFirmwareVersion()

    listener = SyncMultiFrameListener(
        FrameType.Color | FrameType.Ir | FrameType.Depth)

    # Register listeners
    device.setColorFrameListener(listener)
    device.setIrAndDepthFrameListener(listener)

    device.start()

    # Registration
    registration = Registration(device.getIrCameraParams(),
                                device.getColorCameraParams())
    undistorted = Frame(512, 424, 4)
    registered = Frame(512, 424, 4)

    frames = listener.waitForNewFrame()

    color = frames[FrameType.Color]
    ir = frames[FrameType.Ir]
    depth = frames[FrameType.Depth]

    registration.apply(color, depth, undistorted, registered)

    ### Color ###
    assert color.width == 1920
    assert color.height == 1080
    assert color.bytes_per_pixel == 4

    assert ir.width == 512
    assert ir.height == 424
    assert ir.bytes_per_pixel == 4

    assert depth.width == 512
    assert depth.height == 424
    assert depth.bytes_per_pixel == 4

    assert color.asarray().shape == (color.height, color.width, 4)
    assert ir.asarray().shape == (ir.height, ir.width)
    assert depth.astype(np.float32).shape == (depth.height, depth.width)

    def __test_cannot_determine_type_of_frame(frame):
        frame.asarray()

    for frame in [registered, undistorted]:
        yield raises(ValueError)(__test_cannot_determine_type_of_frame), frame

    device.stop()
    device.close()
