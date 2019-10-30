package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import com.ntconcepts.gcpdemo1.utils.CleanForColumnName
import org.apache.beam.sdk.options.ValueProvider
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView

class EncodeCompanyFn(
    val hotEncodeCompany: ValueProvider<Boolean>,
    val companiesView: PCollectionView<List<String>>,
    val companyPrefix: String
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {


    @ProcessElement
    fun apply(c: ProcessContext) {
        val row = c.element().value.copy()
        row.companiesEncoded = row.companiesEncoded?.clone() as HashMap<String, Int>
        val trip = c.element().key

        val companies = c.sideInput(companiesView)

        val cleanedCompany = CleanForColumnName.clean(trip?.company)
        row.company = trip?.company

        //One-hot encode company
        if (hotEncodeCompany.get()) {
            companies.forEach {
                if (it == "${companyPrefix}${cleanedCompany}") {
                    row.companiesEncoded?.put("${companyPrefix}${cleanedCompany}", 1)
                } else {
                    row.companiesEncoded?.put(it, 0)
                }
            }
        }

        c.output(KV.of(trip, row))
    }


}