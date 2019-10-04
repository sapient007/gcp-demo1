package com.ntconcepts.gcpdemo1;

import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.gcp.bigquery.BigQueryIO;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;

public class LoadToBigquery {

//    public static PCollection<KV<String, String>> write(PCollection<KV<String, String>> p) {
//        p.apply("Load transformed trips",
//                BigQueryIO.write()
//                .to("chicagotaxi.finaltaxi_encoded_el_test")
//                );
//    }

}
