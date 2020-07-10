from django.contrib.auth.models import User

from experiments import auth, RowT
from experiments.constants import *
from experiments.helpers import get_obj_id_from_name
from experiments.models import Channel, Project, Researcher, Slide, Technology

from experiments.tests.helpers import (
    ExcelRowInfoGenerator,
    MeasurementImportBaseTestCase,
)
from experiments.xls.measurement_importer import MeasurementImporter


class MeasurementImportTestCase(MeasurementImportBaseTestCase):
    
    def test_create_with_one_slot(self):
        row = ExcelRowInfoGenerator.get_sample_row()
        MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_in_database(row)

    def test_update_with_one_slot(self):
        original_row = ExcelRowInfoGenerator.get_sample_row()
        MeasurementImporter(original_row, self.user_id).import_measurement()
        self.check_row_is_in_database(original_row)
        ch1 = Channel.objects.get_or_create(name="channel1")[0]
        ch2 = Channel.objects.get_or_create(name="channel2")[0]
        t1 = "t1"
        t2 = "t2"
        t3 = "t3"
        new_row = {
            RESEARCHER: str(Researcher.objects.last()),
            PROJECT: str(Project.objects.last()),
            TECHNOLOGY: str(Technology.objects.last()),
            MEASUREMENT_NUMBER: original_row[MEASUREMENT_NUMBER],
            DATE: original_row[DATE],
            AUTOMATED_PLATEID: original_row.get(AUTOMATED_PLATEID),
            AUTOMATED_SLIDEN: original_row[AUTOMATED_SLIDEN],
            SLIDE_ID: original_row[SLIDE_ID],
            SLIDE_BARCODE: "4",
            IMAGE_CYCLE: 4,
            TISSUE1: "some",
            SAMPLE1: "some",
            AGE1: "age1",
            TISSUE2: "some2",
            SAMPLE2: "some2",
            GENOTYPE2: "genotype2",
            TISSUE3: "some3",
            SAMPLE3: "some3",
            AGE3: "some3",
            CHANNEL1: str(ch1),
            TARGET1: str(t1),
            CHANNEL2: str(ch2),
            TARGET2: str(t2),
            CHANNEL3: str(ch1),
            TARGET3: str(t2),
            CHANNEL4: str(ch2),
            TARGET4: str(t3),
            CHANNEL5: str(ch2),
            TARGET5: str(t3),
            LOW_MAG_REFERENCE: "some",
            MAG_BIN_OVERLAP: "some",
            SECTION_NUM: "2, 3",
            ZPLANES: "some",
            NOTES_1: "SMTH2",
            NOTES_2: "SMTH2",
            POST_STAIN: "smth2",
            HARMONY_COPY: "No",
            EXPORT_LOCATION: "some",
            ARCHIVE_LOCATION: "some",
            TEAM_DIR: "some",
            EXPORTED: "No"
        }
        MeasurementImporter(new_row, self.user_id).import_measurement()
        self.check_row_is_in_database(new_row)
        self.check_row_is_not_in_database(original_row)

    def test_append_new_slot_to_existing_automated_measurement(self):
        """
        Create an automated measurement.
        Create a row with the same measurement, different SlideID and samples
        Both rows must belong to the same measurement.
        """
        row = ExcelRowInfoGenerator.get_sample_row()
        m1 = MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_in_database(row)
        new_row_info = {
            SLIDE_BARCODE: str(Slide.objects.first().barcode),
            AUTOMATED_SLIDEN: 2,
            SLIDE_ID: "slide_2",
            TISSUE1: "slide_2",
            SAMPLE1: "slide_2",
            TISSUE2: "slide_2_1",
            SAMPLE2: "slide_2_1",
        }
        new_row = row.copy()
        new_row.update(new_row_info)
        m2 = MeasurementImporter(new_row, self.user_id).import_measurement()
        self.check_row_is_in_database(new_row)
        self.assertEqual(m1.id, m2.id)

    def test_incorrect_new_slot_for_existing_automated_measurement(self):
        """If slot contains a different measurement info, it should be dismissed"""
        pass

    def test_append_new_slot_to_existing_manual_measurement(self):
        row = ExcelRowInfoGenerator.get_sample_row()
        m1 = MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_in_database(row)
        new_row_info = {
            SLIDE_BARCODE: str(Slide.objects.last().barcode),
            AUTOMATED_SLIDEN: 2,
            TISSUE1: "slide_2",
            SAMPLE1: "slide_2",
            TISSUE2: "slide_2_1",
            SAMPLE2: "slide_2_1",
        }
        new_row = row.copy()
        new_row.update(new_row_info)
        m2 = MeasurementImporter(new_row, self.user_id).import_measurement()
        self.check_row_is_in_database(new_row)
        self.assertEqual(m1.id, m2.id)

    def test_authorized_creation_for_roles(self):
        """
        Test that a user with owner role on a project can create a measurement.
        Test that a user with viewer role on a project cannot create a measurement. 
        Test a user without any role on a project cannot create a measurement.
        """
        row = ExcelRowInfoGenerator.get_sample_row()
        user = User.objects.create(username="Some", password="some")
        authorized_project_name = row[PROJECT]
        auth.add_role(user.id, get_obj_id_from_name("project", authorized_project_name), Role.OWNER)
        MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_in_database(row)

        project_without_role = Project.objects.create(name="project_without_role")
        self.check_project_cannot_be_created(row.copy(), project_without_role)

        auth.add_role(self.user_id, project_without_role.id, Role.VIEWER)
        self.check_project_cannot_be_created(row.copy(), project_without_role)
    
    def check_project_cannot_be_created(self, row: RowT, unauthorized_project: Project) -> None:
        assert not auth.check_permission(self.user_id, unauthorized_project.id, CREATE_OR_UPDATE_PERMISSION)
        row[PROJECT] = unauthorized_project.name
        row[MEASUREMENT_NUMBER] = "some"
        with self.assertRaises(PermissionError):
            MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_not_in_database(row)

    def test_authorized_deletion_for_roles(self):
        """
        Test that an owner user on a project can delete a measurement. 
        Test that a viewer or anonymous user on a project cannot delete a measurement.
        """
        row = ExcelRowInfoGenerator.get_sample_row()
        project_id = get_obj_id_from_name("project", row[PROJECT])
        MeasurementImporter(row, self.user_id).import_measurement()
        self.check_row_is_in_database(row)

        # check viewer
        viewer = User.objects.create(username="viewer", password="simple")
        auth.add_role(viewer.id, project_id, Role.VIEWER)
        self.try_deleting_row_and_check_it_was_not_deleted(viewer, project_id, row)

        # check anonymous
        auth.remove_existing_role(viewer.id, project_id)
        self.try_deleting_row_and_check_it_was_not_deleted(viewer, project_id, row)

        # check owner
        MeasurementImporter(row, self.user_id).delete_measurement()
        self.check_row_is_not_in_database(row)

    def try_deleting_row_and_check_it_was_not_deleted(self, user: User, project_id: int, row: RowT):
        assert not auth.check_permission(user.id, project_id, DELETE_PERMISSION)
        with self.assertRaises(PermissionError):
            MeasurementImporter(row, user.id).delete_measurement()
        self.check_row_is_in_database(row)
