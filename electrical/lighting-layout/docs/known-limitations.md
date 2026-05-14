# Known Limitations — lighting-layout

- Uniformity (Emin/Eavg) not calculated — point-by-point calculation requires photometric IES/LDT files
- UGR not numerically calculated — requires luminaire luminance data
- No emergency lighting autonomy calculation (see emergency-lighting skill)
- DALI address assignment not generated — handled by controls engineer
- Daylight factor calculation not included — use daylighting skill
- Reflectance values assumed from standard table unless photometric data provided
