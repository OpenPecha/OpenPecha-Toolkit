from pathlib import Path

from openpecha.formatters import HFMLFormatter, TsadraFormatter
from openpecha.serializers import EpubSerializer, HFMLSerializer

if __name__ == "__main__":

    ebook_path = "./output/demo/src/P000111/OEBPS/"
    opfs_path = "./output/demo/output"
    opf_path = "./output/demo/output/P000111/P000111.opf/"
    hfml_path = "./output/demo/output/P000111_hfml"
    ebook_output_path = "./output/demo/output/ebooks"
    pecha_id = 111
    pecha_name = f"P{pecha_id:06}"

    # 1. Format Tsadra Ebook to OPF (OpenPecha Format)
    formatter = TsadraFormatter(output_path=opfs_path)
    formatter.create_opf(ebook_path, pecha_id)

    # 2. Serialize OPF to HFML (Human Friendly Markup Language)
    serializer = HFMLSerializer(opf_path)
    serializer.apply_layers()
    results = serializer.get_result()
    for vol_id, hfml_text in results.items():
        Path(f"{hfml_path}/{vol_id}.txt").write_text(hfml_text)

    # 3. Format HFML to OPF
    formatter = HFMLFormatter(output_path=opfs_path)
    formatter.create_opf(hfml_path, pecha_id)

    # 4. Convert OPF to Ebook
    serializer = EpubSerializer(Path(opf_path))
    serializer.apply_layers()
    serializer.serialize(ebook_output_path)
