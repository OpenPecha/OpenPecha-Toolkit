import os
import re
import shutil
import zipfile
from bs4 import BeautifulSoup
from pathlib import Path

import requests
import yaml

from openpecha.formatters.layers import AnnType

from .serialize import Serialize


class PedurmaSerializer(Serialize):
    """Pedurma serializer class to get diplomatic text."""

    def __get_adapted_span(self, span, vol_id):
        """Adapts the annotation span to base-text of the text

        Adapts the annotation span, which is based on volume base-text
        to text base-text.

        Args:
            span (dict): span of a annotation, eg: {start:, end:}
            vol_id (str): id of vol, where part of the text exists.

        Returns:
            adapted_start (int): adapted start based on text base-text
            adapted_end (int): adapted end based on text base-text

        """
        adapted_start = span["start"] - self.text_spans[vol_id]["start"]
        adapted_end = span["end"] - self.text_spans[vol_id]["start"]
        return adapted_start, adapted_end

    def apply_annotation(self, vol_id, ann, uuid2localid):
        """Applies annotation to specific volume base-text, where part of the text exists.

        Args:
            vol_id (str): id of vol, where part of the text exists.
            ann (dict): annotation of any type.

        Returns:
            None

        """
        only_start_ann = False
        start_payload = "("
        end_payload = ")"
        if ann["type"] == AnnType.pagination:
            start_payload = ''
            end_payload = f'<p{ann["span"]["vol"]}-{ann["page_num"]}>'
        elif ann["type"] == AnnType.pedurma_note:
            start_payload = ":"
            end_payload = f'{ann["note"]}'
        

        start_cc, end_cc = self.__get_adapted_span(ann["span"], vol_id)
        self.add_chars(vol_id, start_cc, True, start_payload)
        if not only_start_ann:
            self.add_chars(vol_id, end_cc, False, end_payload)

    def get_chunks(self, text):
        result = []
        cur_note = []
        chunks = re.split('(\{.+?\})', text)
        for chunk in chunks:
            if '{' in chunk:
                note = yaml.safe_load(chunk)
                cur_note.append(note)
                result.append(cur_note)
                cur_note = []
            else:
                cur_note.append(chunk)
        result.append([chunk, {}])
        return result
    
    def process_chunk(self, chunk, pub):
        chunk_text = chunk[0]
        chunk_notes = chunk[1]
        if chunk_notes:
            note = chunk_notes[pub]
            old_note = re.search('(:\S+)\n?', chunk_text).group(1)
            chunk_text = re.sub(old_note, note, chunk_text)
        return chunk_text

    def get_diplomatic_text(self, text, pub):
        diplomatic_text = ""
        chunks = self.get_chunks(text)
        for chunk in chunks:
            diplomatic_text += self.process_chunk(chunk, pub)
        return diplomatic_text

    def serialize(self, output_path="./output/diplomatic_text/", pub='pe'):
        output_path = Path(output_path)
        self.apply_layers()
        results = self.get_result()
        for vol_id, result in results.items():
            result = result.replace('::',":")
            diplomatic_text = self.get_diplomatic_text(result, pub)
            (output_path / vol_id).write_text(diplomatic_text, encoding='utf-8')
        print('Serialize complete...')