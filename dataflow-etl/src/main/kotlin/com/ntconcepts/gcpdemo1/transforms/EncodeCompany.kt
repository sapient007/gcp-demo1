package com.ntconcepts.gcpdemo1.transforms

import com.google.api.services.bigquery.model.TableRow
import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.utils.CleanForColumnName
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView

class EncodeCompany(val companiesView: PCollectionView<List<String>>, val companyPrefix: String) :
    DoFn<KV<TaxiRideL1, TableRow>, KV<TaxiRideL1, TableRow>>() {


    @ProcessElement
    fun apply(c: ProcessContext) {
        val row = c.element().value.clone()
        val trip = c.element().key

        val companies = c.sideInput(companiesView)

        val cleanedCompany = CleanForColumnName.clean(trip?.company)

        //One-hot encode company
        companies.forEach {
            if (it == "${companyPrefix}${cleanedCompany}") {
                row.set("${companyPrefix}${cleanedCompany}", 1)
            } else {
                row.set(it, 0)
            }
        }

        row.set("company", trip?.company)
        c.output(KV.of(trip, row))
    }


}