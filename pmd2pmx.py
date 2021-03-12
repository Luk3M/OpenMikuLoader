import pymeshio.converter
import pymeshio.pmx.writer
import pymeshio.pmd.reader
import argparse, os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("pmd", help="path to a Polygon Model Data file (.pmd).")
    parser.add_argument("pmx", help="destination path to the Polygon Model eXtended file (.pmx) that will be created.")
    args = parser.parse_args()

    m = pymeshio.pmd.reader.read_from_file(args.pmd)
    pmx_model = pymeshio.converter.pmd_to_pmx(m)
    pymeshio.pmx.writer.write_to_file(pmx_model, args.pmx)
    print(f"{args.pmd} successfully converted to .pmx in {args.pmx}")
