import tempfile
from pathlib import Path

from test_data_provider import HOCRIATestFileProvider
from openpecha.formatters.ocr.hocr import HOCRFormatter

from openpecha.utils import load_yaml, dump_yaml



def test_base_text():
    work_id = "W22084"
    pecha_id = "I9876543"
    mode = "IA"
    
    ocr_path = Path(__file__).parent / "data" / "file_per_volume" / work_id
    expected_base_text = (Path(__file__).parent / "data" / "file_per_volume" / "opf_expected_datas" / "expected_base_text.txt").read_text(encoding='utf-8')
    buda_data_path = Path(__file__).parent / "data" / "file_per_volume" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "file_per_volume" / "ocr_import_info.yml"
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    bdrc_image_list_path = Path(__file__).parent / "data" / "file_per_volume" / work_id 
    data_provider = HOCRIATestFileProvider(work_id, bdrc_image_list_path, buda_data, ocr_import_info, ocr_path)
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdirname = Path(f"./")
        formatter = HOCRFormatter(mode=mode, output_path=tmpdirname)
        pecha_path = formatter.create_opf(data_provider, pecha_id, {}, ocr_import_info)
        base_text = (pecha_path / f"{pecha_path.name}.opf" / "base" / "I0886.txt").read_text(encoding='utf-8')
        assert expected_base_text == base_text

def test_build_layers():
    work_id = "W22084"
    pecha_id = "I9876543"
    mode = "IA"
    
    ocr_path = Path(__file__).parent / "data" / "file_per_volume" / work_id
    expected_pagination_layer = load_yaml((Path(__file__).parent / "data" / "file_per_volume" / "opf_expected_datas" / "expected_Pagination.yml"))
    expected_confidence_layer = load_yaml((Path(__file__).parent / "data" / "file_per_volume" / "opf_expected_datas" / "expected_OCRConfidence.yml"))
    buda_data_path = Path(__file__).parent / "data" / "file_per_volume" / "buda_data.yml"
    ocr_import_info_path = Path(__file__).parent / "data" / "file_per_volume" / "ocr_import_info.yml"
    ocr_import_info = load_yaml(ocr_import_info_path)
    buda_data = load_yaml(buda_data_path)
    image_list_path = Path(__file__).parent / "data" / "file_per_volume" / work_id
    data_provider = HOCRIATestFileProvider(work_id, image_list_path, buda_data, ocr_import_info, ocr_path)

    opf_options = {"ocr_confidence_threshold": 0.9, "max_low_conf_per_page": 50}
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        formatter = HOCRFormatter(mode=mode, output_path=tmpdirname)
        pecha_path = formatter.create_opf(data_provider, pecha_id, opf_options, ocr_import_info)
        pagination_layer = load_yaml((pecha_path / f"{pecha_path.name}.opf" / "layers" / "I0886" / "Pagination.yml"))
        confidence_layer = load_yaml((pecha_path / f"{pecha_path.name}.opf" / "layers" / "I0886" / "OCRConfidence.yml"))

        ###Pagination layer testing
        for (_, expected_ann), (_, ann) in zip(expected_pagination_layer['annotations'].items(), pagination_layer['annotations'].items()):
            assert expected_ann == ann

        ###Confidence layer testing
        for (_, expected_ann), (_, ann) in zip(expected_confidence_layer['annotations'].items(), confidence_layer['annotations'].items()):
            assert expected_ann == ann

if __name__ == "__main__":
    test_base_text()
    test_build_layers()