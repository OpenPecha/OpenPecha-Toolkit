from pathlib import Path
from openpecha.core.layer import LayerEnum
from openpecha.serializers.serialize import Serialize


def micro_to_milliseconds(microseconds):
    return microseconds // 1000


class ElanSerializer(Serialize):
    """Elan serializer class to get .eaf file."""

    def __init__(
        self, opf_path, text_id=None, base_ids=None, layers=None, index_layer=None
    ):
        super().__init__(opf_path, text_id, base_ids, layers, index_layer)
        self.annotation_sequence = {}
        self.time_order = {}

    def apply_annotation(self, base_id, annotation, uuid2localid):

        ann_type = LayerEnum(annotation["type"])
        if ann_type == LayerEnum.transcription_time_span:
            if base_id not in self.annotation_sequence:
                self.annotation_sequence[base_id] = 1
            start_payload = """        <ANNOTATION>
            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a{seq}"
                TIME_SLOT_REF1="ts{slot1}" TIME_SLOT_REF2="ts{slot2}">
                <ANNOTATION_VALUE>""".format(
                seq=self.annotation_sequence[base_id],
                slot1=self.annotation_sequence[base_id] * 2 - 1,
                slot2=self.annotation_sequence[base_id] * 2,
            )
            end_payload = """</ANNOTATION_VALUE>
            </ALIGNABLE_ANNOTATION>
        </ANNOTATION>"""
            self.add_chars(base_id, annotation["span"]["start"], True, start_payload)
            self.add_chars(base_id, annotation["span"]["end"], True, end_payload)
            if base_id not in self.time_order:
                self.time_order[
                    base_id
                ] = f"""        <TIME_SLOT TIME_SLOT_ID="ts{self.annotation_sequence[base_id] * 2 - 1}" TIME_VALUE="{micro_to_milliseconds(annotation["time_span"]["start"])}"/>
        <TIME_SLOT TIME_SLOT_ID="ts{self.annotation_sequence[base_id] * 2}" TIME_VALUE="{micro_to_milliseconds(annotation["time_span"]["end"])}"/>"""
            else:
                self.time_order[
                    base_id
                ] += f"""
        <TIME_SLOT TIME_SLOT_ID="ts{self.annotation_sequence[base_id] * 2 - 1}" TIME_VALUE="{micro_to_milliseconds(annotation["time_span"]["start"])}"/>
        <TIME_SLOT TIME_SLOT_ID="ts{self.annotation_sequence[base_id] * 2}" TIME_VALUE="{micro_to_milliseconds(annotation["time_span"]["end"])}"/>"""
            self.annotation_sequence[base_id] += 1

    def get_elan(self, base_id, result):
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<ANNOTATION_DOCUMENT AUTHOR="" DATE="2023-03-15T20:50:48+05:30"
    FORMAT="3.0" VERSION="3.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.mpi.nl/tools/elan/EAFv3.0.xsd">
    <HEADER MEDIA_FILE="" TIME_UNITS="milliseconds">
        <MEDIA_DESCRIPTOR
            MEDIA_URL="file:///Users/spsither/Documents/OpenPecha/OTR002-Output/OTR002-01-གངས་རིན་པོ་ཆེ།/OTR001.wav"
            MIME_TYPE="audio/x-wav" RELATIVE_MEDIA_URL="./OTR001.wav"/>
        <PROPERTY NAME="URN">urn:nl-mpi-tools-elan-eaf:ea97e0c9-0c39-48c0-be65-ae73b74d1be1</PROPERTY>
        <PROPERTY NAME="lastUsedAnnotationId">4</PROPERTY>
    </HEADER>
    <TIME_ORDER>
{self.time_order[base_id]}
    </TIME_ORDER>
    <TIER LINGUISTIC_TYPE_REF="default-lt" TIER_ID="default">
{result}    </TIER>
    <LINGUISTIC_TYPE GRAPHIC_REFERENCES="false"
        LINGUISTIC_TYPE_ID="default-lt" TIME_ALIGNABLE="true"/>
    <CONSTRAINT
        DESCRIPTION="Time subdivision of parent annotation's time interval, no time gaps allowed within this interval" STEREOTYPE="Time_Subdivision"/>
    <CONSTRAINT
        DESCRIPTION="Symbolic subdivision of a parent annotation. Annotations refering to the same parent are ordered" STEREOTYPE="Symbolic_Subdivision"/>
    <CONSTRAINT DESCRIPTION="1-1 association with a parent annotation" STEREOTYPE="Symbolic_Association"/>
    <CONSTRAINT
        DESCRIPTION="Time alignable annotations within the parent annotation's time interval, gaps are allowed" STEREOTYPE="Included_In"/>
</ANNOTATION_DOCUMENT>
"""

    def serialize(self, output_path="./output"):
        output_path = Path(output_path)
        self.apply_layers()
        results = self.get_result()
        elan_files = []
        for base_id, result in results.items():
            output_path.mkdir(exist_ok=True, parents=True)
            (output_path / f"{base_id}.eaf").write_text(
                self.get_elan(base_id, result), encoding="utf-8"
            )
            elan_files += [output_path / f"{base_id}.eaf"]
        return elan_files
