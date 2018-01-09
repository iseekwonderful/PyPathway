# This file perform the necessary network downloading from the tests
# this part can be ignored, if so, several test will failed due to the stdout, than re-run it


from pypathway import IdMapping, STRING, BioGRID
import wget
import os

if __name__ == '__main__':
    print("Start download Database for testing")
    IdMapping.check_db_available("hsa")
    print("Start download obo file")
    if not os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/analysis/go.obo"):
        wget.download('http://purl.obolibrary.org/obo/go/go-basic.obo', os.path.dirname(os.path.realpath(__file__)) + "/analysis/go.obo")
    print("Start to cache string and biogrid")
    STRING.overall_graph("hsa")
    BioGRID.overall_graph('hsa')