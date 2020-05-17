select experiments_measurement.id as measurement_id, experiments_researcher.login as researcher, experiments_project.name as project,
 pl.name as automated_plate_id, asl.name as automated_slide_id, slot.automated_slide_num, 
experiments_measurement.image_cycle, sb.name as slide_barcode,
string_agg(distinct concat(sec.number, ' | ', experiments_sample.name, ' | ', experiments_tissue.name, ' | ', experiments_age.name, ' | ', experiments_genotype.name, ' | ', experiments_background.name), ';; ') as samples,
experiments_technology.name as technology,
string_agg(concat(experiments_channel.name, ' -> ', experiments_target.name), ';; ') as channel_targets,
experiments_measurement.date, mn.name as measurement_number, lmr.name as low_mag_reference, mbo.name as mag_bin_overlap, zplanes.name as zplanes, experiments_measurement.notes_1, experiments_measurement.notes_2, experiments_measurement.post_stain, experiments_measurement.harmony_copy_deleted,
el.name as export_location,
al.name as archive_location, td.name as team_directory, concat('http://imaging-tracker.cellgeni.sanger.ac.uk/admin/experiments/measurement/', experiments_measurement.id, '/change/') as url
from experiments_slot as slot
left join experiments_measurement on experiments_measurement.id = slot.measurement_id
left join experiments_automatedslide as asl on asl.id = slot.automated_slide_id
left join experiments_slot_sections as ess on ess.slot_id = slot.id
left join experiments_section as sec on ess.section_id = sec.id
left join experiments_slide as sl on sec.slide_id = sl.id
left join experiments_slidebarcode as sb on sb.id = sl.barcode_id
left join experiments_sample on sec.sample_id = experiments_sample.id
left join experiments_tissue on experiments_sample.tissue_id = experiments_tissue.id
left join experiments_age on experiments_sample.age_id = experiments_age.id
left join experiments_background on experiments_sample.background_id = experiments_background.id
left join experiments_genotype on experiments_sample.genotype_id = experiments_genotype.id
left join experiments_researcher on experiments_measurement.researcher_id = experiments_researcher.id
left join experiments_project on experiments_measurement.project_id = experiments_project.id
left join experiments_plate as pl on experiments_measurement.plate_id = pl.id
left join experiments_technology on experiments_measurement.technology_id = experiments_technology.id
left join experiments_measurement_channel_target_pairs as mctp on mctp.measurement_id = experiments_measurement.id
left join experiments_channeltarget as cht on mctp.channeltarget_id = cht.id
left join experiments_channel on cht.channel_id = experiments_channel.id
left join experiments_target on cht.target_id = experiments_target.id
left join experiments_measurementnumber as mn on mn.id = experiments_measurement.measurement_number_id
left join experiments_lowmagreference as lmr on lmr.id = experiments_measurement.low_mag_reference_id
left join experiments_magbinoverlap as mbo on mbo.id = experiments_measurement.mag_bin_overlap_id
left join experiments_zplanes as zplanes on zplanes.id = experiments_measurement.z_planes_id
left join experiments_teamdirectory as td on td.id = experiments_measurement.team_directory_id
left join experiments_exportlocation as el on el.id = experiments_measurement.export_location_id
left join experiments_archivelocation as al on al.id = experiments_measurement.archive_location_id
where true [[ and {{project}} ]] [[and {{authorized_projects}}]] [[ and {{researcher}} ]]
[[ and asl.name like concat('%', {{automated_slide_id}}, '%') ]] [[ and pl.name like concat('%', {{automated_plate_id}}, '%') ]] [[ and {{automated_slide_num}} ]]
[[ and {{image_cycle}} ]] [[ and experiments_sample.name like concat('%', {{sample_id}}, '%') ]] [[ and {{tissue}} ]]
[[ and {{age}} ]] [[ and {{genotype}} ]] [[ and {{background}} ]] [[ and sb.name like concat('%', {{ slide_barcode }}, '%') ]]  [[ and {{ technology }} ]] [[ and {{ channel }} ]]
[[ and {{ target }} ]] [[ and experiments_measurement.date >= {{fromdate}} ]] [[ and experiments_measurement.date <= {{untildate}} ]] [[ and {{ measurement_number }}]] [[ and {{ mag_bin_overlap }}]]
[[ and {{ low_mag_reference }}]] [[ and td.name like concat('%', {{ team_directory }}, '%') ]] [[ and el.name like concat('%', {{export_location}}, '%') ]]
[[ and al.name like concat('%', {{archive_location}}, '%') ]] [[ and {{ meas_id }}]]
group by experiments_measurement.id, slot.automated_slide_num, experiments_researcher.login, experiments_project.name, 
experiments_technology.name, asl.name, pl.name, 
experiments_measurement.image_cycle, sb.id, el.id, al.id,
experiments_measurement.date, mn.name, lmr.name, mbo.name, zplanes.name, experiments_measurement.notes_1, experiments_measurement.notes_2, experiments_measurement.export_location_id,
experiments_measurement.archive_location_id, td.name; 