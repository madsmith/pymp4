#!/usr/bin/env python
"""
   Copyright 2016 beardypig

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
import logging
import unittest

from construct import Container
from pymp4.parser import Box

log = logging.getLogger(__name__)


class BoxTests(unittest.TestCase):
    def test_ftyp_parse(self):
        self.assertEqual(
            Box.parse(b'\x00\x00\x00\x18ftypiso5\x00\x00\x00\x01iso5avc1'),
            Container(offset=0)
            (type=b"ftyp")
            (major_brand=b"iso5")
            (minor_version=1)
            (compatible_brands=[b"iso5", b"avc1"])
            (end=24)
        )

    def test_ftyp_build(self):
        self.assertEqual(
            Box.build(dict(
                type=b"ftyp",
                major_brand=b"iso5",
                minor_version=1,
                compatible_brands=[b"iso5", b"avc1"])),
            b'\x00\x00\x00\x18ftypiso5\x00\x00\x00\x01iso5avc1')

    def test_mdhd_parse(self):
        self.assertEqual(
            Box.parse(
                b'\x00\x00\x00\x20mdhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00U\xc4\x00\x00'),
            Container(offset=0)
            (type=b"mdhd")(version=0)(flags=0)
            (creation_time=0)
            (modification_time=0)
            (timescale=1000000)
            (duration=0)
            (language="und")
            (end=32)
        )

    def test_mdhd_build(self):
        mdhd_data = Box.build(dict(
            type=b"mdhd",
            creation_time=0,
            modification_time=0,
            timescale=1000000,
            duration=0,
            language=u"und"))
        self.assertEqual(len(mdhd_data), 32)
        self.assertEqual(mdhd_data,
                         b'\x00\x00\x00\x20mdhd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00U\xc4\x00\x00')

        mdhd_data64 = Box.build(dict(
            type=b"mdhd",
            version=1,
            creation_time=0,
            modification_time=0,
            timescale=1000000,
            duration=0,
            language=u"und"))
        self.assertEqual(len(mdhd_data64), 44)
        self.assertEqual(mdhd_data64,
                         b'\x00\x00\x00,mdhd\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0fB@\x00\x00\x00\x00\x00\x00\x00\x00U\xc4\x00\x00')

    def test_moov_build(self):
        moov = \
            Container(type=b"moov")(children=[  # 96 bytes
                Container(type=b"mvex")(children=[  # 88 bytes
                    Container(type=b"mehd")(version=0)(flags=0)(fragment_duration=0),  # 16 bytes
                    Container(type=b"trex")(track_ID=1),  # 32 bytes
                    Container(type=b"trex")(track_ID=2),  # 32 bytes
                ])
            ])

        moov_data = Box.build(moov)

        self.assertEqual(len(moov_data), 96)
        self.assertEqual(
            moov_data,
            b'\x00\x00\x00\x60moov'
            b'\x00\x00\x00\x58mvex'
            b'\x00\x00\x00\x10mehd\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x20trex\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x20trex\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        )

    def test_smhd_parse(self):
        in_bytes = b'\x00\x00\x00\x10smhd\x00\x00\x00\x00\x00\x00\x00\x00'
        self.assertEqual(
            Box.parse(in_bytes + b'padding'),
            Container(offset=0)
            (type=b"smhd")(version=0)(flags=0)
            (balance=0)(reserved=0)(end=len(in_bytes))
        )

    def test_smhd_build(self):
        smhd_data = Box.build(dict(
            type=b"smhd",
            balance=0))
        self.assertEqual(len(smhd_data), 16),
        self.assertEqual(smhd_data, b'\x00\x00\x00\x10smhd\x00\x00\x00\x00\x00\x00\x00\x00')

    def test_stsd_parse(self):
        tx3g_data = b'\x00\x00\x00\x00\x01\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x12\xFF\xFF\xFF\xFF\x00\x00\x00\x12ftab\x00\x01\x00\x01\x05Serif'
        in_bytes = b'\x00\x00\x00\x50stsd\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x40tx3g\x00\x00\x00\x00\x00\x00\x00\x01' + tx3g_data
        self.assertEqual(
            Box.parse(in_bytes + b'padding'),
            Container(offset=0)
            (type=b"stsd")(version=0)(flags=0)
            (entries=[Container(format=b'tx3g')(data_reference_index=1)(data=tx3g_data)])
            (end=len(in_bytes))
        )

    def test_hdlr_parse(self):
        generic_sound_media_handler = b'\x00\x00\x00\x30\x68\x64\x6C\x72\x00\x00\x00\x00\x00\x00\x00\x00\x73\x6F\x75\x6E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x47\x65\x6E\x65\x72\x69\x63\x20\x48\x61\x6E\x64\x6C\x65\x72\x00'
        # Some files have been found to use PascalStrings and not be null terminated, causing the parse to crash
        apple_sound_media_handler = b'\x00\x00\x00\x3A\x68\x64\x6C\x72\x00\x00\x00\x00\x00\x00\x00\x00\x73\x6F\x75\x6E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x19\x41\x70\x70\x6C\x65\x20\x53\x6F\x75\x6E\x64\x20\x4D\x65\x64\x69\x61\x20\x48\x61\x6E\x64\x6C\x65\x72'
        video_handler = b'\x00\x00\x00\x2D\x68\x64\x6C\x72\x00\x00\x00\x00\x00\x00\x00\x00\x76\x69\x64\x65\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x56\x69\x64\x65\x6F\x48\x61\x6E\x64\x6C\x65\x72\x00'

        self.assertEqual(
            Box.parse(generic_sound_media_handler),
            Container(offset=0)
            (type=b'hdlr')
            (version=0)
            (flags=0)
            (handler_type=b"soun")
            (name="Generic Handler")
            (end=48)
        )

        self.assertEqual(
            Box.parse(apple_sound_media_handler),
            Container(offset=0)
            (type=b'hdlr')
            (version=0)
            (flags=0)
            (handler_type=b"soun")
            (name="\x19Apple Sound Media Handler")
            (end=58)
        )

        self.assertEqual(
            Box.parse(video_handler),
            Container(offset=0)
            (type=b"hdlr")
            (version=0)
            (flags=0)
            (handler_type=b"vide")
            (name="VideoHandler")
            (end=45)
        )


    def test_dref_parse(self):
        dref_alis = b'\x00\x00\x00\x1Cdref\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0Calis\x00\x00\x00\x01'

        self.assertEqual(
            Box.parse(dref_alis),
            Container(offset=0)
            (type=b'dref')
            (version=0)
            (flags=0)
            (data_entries=[Container(offset=16)(type=b'alis')(data=b'\x00\x00\x00\x01')(end=28)])
            (end=28)
        )

