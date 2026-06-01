# LocalPulse
# LocalPulse 🏙️
### A Neighborhood Feature Store built with Python and SQL

A production-style data engineering project that ingests live weather, 
crime, and school quality data across US cities, engineers ML-ready 
features using SQL, and serves them through a versioned Python interface.

---

## What It Does

LocalPulse simulates the kind of infrastructure real ML teams depend on — 
a reliable, versioned source of clean features that any downstream model 
or analyst can query without re-engineering the pipeline themselves.

Every time the pipeline runs it:
1. Pulls live data from 3 public sources via REST APIs
2. Cleans and transforms raw data into engineered features using SQL
3. Joins all sources into a master feature table
4. Scores each city on liveability using a composite SQL model
5. Stores everything in a versioned feature registry

---

## Architecture