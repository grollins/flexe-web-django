import logging
from os.path import join
from celery import shared_task
from time import sleep
from tempfile import mkdtemp
from shutil import copyfile, rmtree

from flexe import FlexE

from .models import Job, Result

@shared_task()
def run_flexe_calculation(job_id):
    job = Job.objects.get(pk=job_id)
    temp_dir = mkdtemp()
    temp_ref_path = join(temp_dir, 'ref.pdb')
    temp_comparison_path = join(temp_dir, 'comparison.pdb')
    copyfile(job.reference.path, temp_ref_path)
    copyfile(job.comparison.path, temp_comparison_path)
    logging.info( "%s %s" % (temp_ref_path, temp_comparison_path))
    try:
        f = FlexE(ref_pdb_file=temp_ref_path)
        output = f.compare_with_ref(pdb_file=temp_comparison_path)
        create_result_obj(job, output)
        job.status = Job.STATUS.done
    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        job.status = Job.STATUS.error
        job.error_message = error_message

    sleep(10.) # seconds
    job.save()
    rmtree(temp_dir)
    return

def create_result_obj(job, output):
    rmsd, energy_ref_to_pdb, energy_pdb_to_ref = output
    r = Result.objects.create(job=job, rmsd=rmsd,
                              energy_ref_to_pdb=energy_ref_to_pdb,
                              energy_pdb_to_ref=energy_pdb_to_ref)
    return
