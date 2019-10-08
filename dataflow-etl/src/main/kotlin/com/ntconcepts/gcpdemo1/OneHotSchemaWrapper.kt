package com.ntconcepts.gcpdemo1

import com.google.cloud.bigquery.StandardSQLTypeName

data class OneHotSchemaWrapper(val keys: List<String>, val bqType: StandardSQLTypeName)