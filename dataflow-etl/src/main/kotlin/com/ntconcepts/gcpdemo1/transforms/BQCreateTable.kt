package com.ntconcepts.gcpdemo1.transforms

import org.apache.beam.sdk.coders.BooleanCoder
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.Create
import org.apache.beam.sdk.transforms.PTransform
import org.apache.beam.sdk.transforms.ParDo
import org.apache.beam.sdk.values.PBegin
import org.apache.beam.sdk.values.PCollectionView
import org.apache.beam.sdk.values.PDone

class BQCreateTable(
    val dataset: ValueProvider<String>,
    val table: ValueProvider<String>,
    val dropTable: ValueProvider<Boolean>,
    val dayOfWeekView: PCollectionView<List<String>>,
    val monthView: PCollectionView<List<String>>,
    val companiesView: PCollectionView<List<String>>,
    val hotEncodeCompany: ValueProvider<Boolean>
) : PTransform<PBegin, PDone>() {


    override fun expand(input: PBegin): PDone {
        //Hack bc passing PBegin wasn't working with ParDo/DoFn
        input.apply(Create.of(true)).setCoder(BooleanCoder.of())
            .apply(
                "CreateTable",
                ParDo.of(
                    CreateBQTable(dataset, table, dropTable, dayOfWeekView, monthView, companiesView, hotEncodeCompany)
                ).withSideInputs(dayOfWeekView, monthView, companiesView)
            )
        return PDone.`in`(input.pipeline)
    }

}