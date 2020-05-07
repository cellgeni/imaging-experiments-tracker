select mes.id as measurement_id, experiments_researcher.login as researcher, experiments_project.name as project,
 pl.name as automated_plate_id, asl.name as automated_slide_id, slot.automated_slide_num,
mes.image_cycle, sb.name as slide_barcode,
string_agg(distinct concat(experiments_sample.name, ' ', experiments_tissue.name, ' ', experiments_age.name, ' ', experiments_genotype.name, ' ', experiments_background.name), '; ') as samples,
experiments_technology.name as technology,
string_agg(distinct concat(experiments_channel.name, ' -> ', experiments_target.name), '; ') as channel_targets,
mes.date, mn.name as measurement_number, lmr.name as low_mag_reference, mbo.name as mag_bin_overlap, zplanes.name as zplanes, mes.notes_1, mes.notes_2, mes.post_stain, mes.harmony_copy_deleted,
el.name as export_location,
al.name as archive_location, td.name as team_directory, concat('http://imaging-tracker.cellgeni.sanger.ac.uk/admin/experiments/measurement/', mes.id, '/change/') as url
from experiments_slot as slot
left join experiments_measurement as mes on mes.id = slot.measurement_id
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
left join experiments_researcher on mes.researcher_id = experiments_researcher.id
left join experiments_project on mes.project_id = experiments_project.id
left join experiments_plate as pl on mes.plate_id = pl.id
left join experiments_technology on mes.technology_id = experiments_technology.id
left join experiments_measurement_channel_target_pairs as mctp on mctp.measurement_id = mes.id
left join experiments_channeltarget as cht on mctp.channeltarget_id = cht.id
left join experiments_channel on cht.channel_id = experiments_channel.id
left join experiments_target on cht.target_id = experiments_target.id
left join experiments_measurementnumber as mn on mn.id = mes.measurement_number_id
left join experiments_lowmagreference as lmr on lmr.id = mes.low_mag_reference_id
left join experiments_magbinoverlap as mbo on mbo.id = mes.mag_bin_overlap_id
left join experiments_zplanes as zplanes on zplanes.id = mes.z_planes_id
left join experiments_teamdirectory as td on td.id = mes.team_directory_id
left join experiments_exportlocation as el on el.id = mes.export_location_id
left join experiments_archivelocation as al on al.id = mes.archive_location_id
where true [[ and {{project}} ]] [[and {{authorized_projects}}]] [[ and {{researcher}} ]]
[[ and {{automated_slide_id}} ]] [[ and {{automated_plate_id}} ]] [[ and {{automated_slide_num}} ]]
[[ and {{image_cycle}} ]] [[ and {{sample_id}} ]] [[ and {{tissue}} ]] [[ and {{plate}} ]]
[[ and {{age}} ]] [[ and {{genotype}} ]] [[ and {{background}} ]] [[ and {{ slide_barcode }} ]]  [[ and {{ technology }} ]] [[ and {{ channel }} ]]
[[ and {{ target }} ]] [[ and mes.date={{date}} ]] [[ and {{ mes_number }}]] [[ and {{ mag_bin_overlap }}]]
[[ and {{ mag_bin_overlap }} ]] [[ and {{ low_mag_reference }}]] [[ and {{ team_directory }}]]
group by mes.id, slot.automated_slide_num, experiments_researcher.login, experiments_project.name,
experiments_technology.name, asl.name, pl.name,
mes.image_cycle, sb.id, el.id, al.id,
mes.date, mn.name, lmr.name, mbo.name, zplanes.name, mes.notes_1, mes.notes_2, mes.export_location_id,
mes.archive_location_id, td.name;