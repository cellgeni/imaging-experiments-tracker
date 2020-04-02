select mes.id as measurement_id, mes.uuid, experiments_researcher.employee_key, experiments_project.key as project,
experiments_technology.name as technology, mes.automated_slide_id, mes.automated_plate_id, mes.automated_slide_num,
mes.image_cycle,
string_agg(distinct concat(experiments_sample.id, ' ', experiments_tissue.name), '; ') as samples,
string_agg(distinct concat(experiments_channel.name, ' -> ', experiments_target.name), '; ') as channel_targets,
mes.date, mn.name as measurement_number, lmr.name as low_mag_reference, mbo.name as mag_bin_overlap, zplanes.name as zplanes, mes.notes_1, mes.notes_2, mes.export_location,
mes.archive_location, td.name as team_directory, concat('http://imaging-tracker.cellgeni.sanger.ac.uk/admin/experiments/measurement/', mes.id, '/change/') as url
from experiments_measurement as mes
left join experiments_measurement_sections as ems on ems.measurement_id = mes.id
left join experiments_section as sec on ems.section_id = sec.id
left join experiments_slide as sl on sec.slide_id = sl.barcode_id
left join experiments_sample on sec.sample_id = experiments_sample.id
left join experiments_tissue on experiments_sample.tissue_id = experiments_tissue.id
left join experiments_researcher on mes.researcher_id = experiments_researcher.employee_key
left join experiments_project on mes.project_id = experiments_project.id
left join experiments_technology on mes.technology_id = experiments_technology.id
left join experiments_measurement_channel_target_pairs as mctp on mctp.measurement_id = mes.id
left join experiments_channeltarget as cht on mctp.channeltarget_id = cht.id
left join experiments_channel on cht.channel_id = experiments_channel.id
left join experiments_target on cht.target_id = experiments_target.id
left join experiments_measurementnumber as mn on mn.id = mes.measurement_id
left join experiments_lowmagreference as lmr on lmr.id = mes.low_mag_reference_id
left join experiments_magbinoverlap as mbo on mbo.id = mes.mag_bin_overlap_id
left join experiments_zplanes as zplanes on zplanes.id = mes.z_planes_id
left join experiments_teamdirectory as td on td.id = mes.team_directory_id
where true [[ and {{project}} ]] [[ and {{researcher}} ]]
[[ and {{automated_slide_id}} ]] [[ and {{automated_plate_id}} ]] [[ and {{automated_slide_num}} ]]
[[ and {{image_cycle}} ]] [[ and {{sample_id}} ]] [[ and {{tissue}} ]]
[[ and {{age}} ]] [[ and {{genotype}} ]] [[ and {{background}} ]]
[[ and {{species}} ]] [[ and {{ slide_barcode }} ]]  [[ and {{ technology }} ]] [[ and {{ channel }} ]]
[[ and {{ target }} ]] [[ and mes.date={{date}} ]] [[ and {{ mes_number }}]] [[ and {{ mag_bin_overlap }}]]
[[ and {{ mag_bin_overlap }} ]] [[ and {{ low_mag_reference }}]] [[ and {{ team_directory }}]]
group by mes.id, experiments_researcher.employee_key, experiments_project.key, mes.uuid,
experiments_technology.name, mes.automated_slide_id, mes.automated_plate_id, mes.automated_slide_num,
mes.image_cycle,
mes.date, mn.name, lmr.name, mbo.name, zplanes.name, mes.notes_1, mes.notes_2, mes.export_location,
mes.archive_location, td.name;