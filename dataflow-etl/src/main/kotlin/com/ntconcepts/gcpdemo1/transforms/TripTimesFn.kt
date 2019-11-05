package com.ntconcepts.gcpdemo1.transforms

import com.ntconcepts.gcpdemo1.models.TaxiRideL1
import com.ntconcepts.gcpdemo1.models.TaxiTripOutput
import org.apache.beam.sdk.transforms.DoFn
import org.apache.beam.sdk.values.KV
import org.apache.beam.sdk.values.PCollectionView
import org.apache.beam.sdk.values.TupleTag
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter

enum class scaleTimes {
    NOON, MIDNIGHT
}

class TripTimesFn(
    private val daysOFWeekView: PCollectionView<List<String>>,
    private val monthsView: PCollectionView<List<String>>,
    private val years: TupleTag<Int>
) :
    DoFn<KV<TaxiRideL1, TaxiTripOutput>, KV<TaxiRideL1, TaxiTripOutput>>() {

    @ProcessElement
    fun apply(c: ProcessContext) {

        val trip = c.element().key
        val row = c.element().value.copy()

        row.start_time_epoch = trip?.trip_start_timestamp as Long / 1000000

        row.daysOfWeekEncoded = row.daysOfWeekEncoded?.clone() as HashMap<String, Int>
        row.monthsEncoded = row.monthsEncoded?.clone() as HashMap<String, Int>

        val daysOfWeek = c.sideInput(daysOFWeekView)
        val months = c.sideInput(monthsView)

        val startTrip: LocalDateTime =
            LocalDateTime.ofEpochSecond(trip.trip_start_timestamp / 1000000, 0, ZoneOffset.UTC)

        val timestampFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")

        row.start_time = startTrip.format(timestampFormatter)
        row.start_time_norm_midnight = normalizeTime(startTrip.toLocalTime(), scaleTimes.MIDNIGHT)
        row.start_time_norm_noon = normalizeTime(startTrip.toLocalTime(), scaleTimes.NOON)

        //One-hot-encode day of the week
        val oheDayOfWeek = "day_of_week_${startTrip.dayOfWeek.name}"
        row.daysOfWeekEncoded?.put(oheDayOfWeek, 1)
        daysOfWeek.forEach {
            if (it != oheDayOfWeek) {
                row.daysOfWeekEncoded?.put(it, 0)
            }
        }
        //One-hot-encode month
        val ohemonth = "month_${startTrip.month.name}"
        row.daysOfWeekEncoded?.put(ohemonth, 1)
        months.forEach {
            if (it != ohemonth) {
                row.daysOfWeekEncoded?.put(it, 0)
            }
        }
        row.year = startTrip.year

        c.output(years, row.year)
        c.output(KV.of(trip, row))
    }

    private val max12_h23: Long = (23 * 3600) + (59 * 60) + 59
    private val min12_h23: Long = (12 * 3600)
    private val min12_h12: Long = (12 * 3600)
    private val max12_h12: Long = 0
    private val max24: Long = (23 * 3600) + (59 * 60) + 59

    private fun normalizeTime(time: LocalTime, scaleTo: scaleTimes): Double {

        //If we're scaling to noon (-1 to 1), 12:00:00 is 0
        if (scaleTo == scaleTimes.NOON && time.hour != 12 && time.minute != 0 && time.second != 0) {
            return 0.0
        }

        val seconds: Double = (time.hour * 3600.0) + (time.minute * 60) + time.second

        return if (scaleTo == scaleTimes.NOON) {
            //If time is > 12:00:00, min is 12:00:00 and max is 23:59:59
            if (time.hour > 12) {
                ((seconds - min12_h23) / (max12_h23 - min12_h23))
            } else {
                //If time is < 12:00:00, min is 12:00:00 and max is 00:00:00
                //Flip the sign for values less than noon for -1 to 0 scaling
                ((seconds - min12_h12) / (max12_h12 - min12_h12)) * -1
            }
        } else {
            // Scale to midnight
            (seconds - 0) / (max24 - 0)
        }

    }


}