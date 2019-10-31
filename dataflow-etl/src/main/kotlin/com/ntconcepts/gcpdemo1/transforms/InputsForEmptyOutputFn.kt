package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.PCollectionView

class InputsForEmptyOutputFn(
    val daysOFWeekView: PCollectionView<List<String>>,
    val monthsView: PCollectionView<List<String>>,
    val companiesView: PCollectionView<List<String>>
) :
    DoFn<TaxiTripOutput, TaxiTripOutput>() {

    @ProcessElement
    fun apply(c: ProcessContext) {

        var out = c.element().copy()

        val daysOfWeek = c.sideInput(daysOFWeekView)
        val months = c.sideInput(monthsView)
        val companies = c.sideInput(companiesView)

        out.daysOfWeekEncoded = out.daysOfWeekEncoded?.clone() as HashMap<String, Int>
        out.monthsEncoded = out.monthsEncoded?.clone() as HashMap<String, Int>
        out.companiesEncoded = out.companiesEncoded?.clone() as HashMap<String, Int>

        daysOfWeek.forEach {
            out.daysOfWeekEncoded?.put(it, 0)
        }

        months.forEach {
            out.daysOfWeekEncoded?.put(it, 0)
        }

        companies.forEach {
            out.companiesEncoded?.put(it, 0)
        }

        c.output(out)


    }
}