package com.ntconcepts.gcpdemo1.utils

object CleanForColumnName {
    fun clean(name: String?): String {
        if (name == null) return ""
        return name.replace(Regex("\\s"), "_")
            .replace(Regex("[^A-Za-z0-9_]"), "")
            .toLowerCase()
    }
}