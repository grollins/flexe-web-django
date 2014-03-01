import logging
from os.path import join, basename
from celery import shared_task
from time import sleep
from tempfile import mkdtemp
from shutil import copyfile, rmtree
from zipfile import ZipFile, is_zipfile
from glob import glob

from flexe import FlexE

from .models import Job, Result

@shared_task()
def run_flexe_calculation(job_id):
    job = Job.objects.get(pk=job_id)
    temp_dir = mkdtemp()
    ref_path = join(temp_dir, 'ref.pdb')
    comparison_path = join(temp_dir, basename(job.comparison.path))
    copyfile(job.reference.path, ref_path)
    copyfile(job.comparison.path, comparison_path)
    logging.info( "%s %s" % (ref_path, comparison_path))

    if comparison_path.endswith('.zip') and is_zipfile(comparison_path):
        # unzip, validate, group files for FlexE calculation
        extract_to = join(temp_dir, 'extracted')
        with ZipFile(comparison_path, 'r') as z:
            pdb_files = [f for f in z.namelist() if f.endswith('.pdb')]
            z.extractall(path=extract_to, members=pdb_files)
        comparison_files = glob( join(extract_to, '*.pdb') )

    elif comparison_path.endswith('.pdb'):
        comparison_files = [comparison_path,]
    
    else:
        job.status = Job.STATUS.error
        job.error_message = "Expected .zip or .pdb, got %s" % \
                            basename(temp_comparison_path)
    
    try:
        for this_comp_file in comparison_files:
            f = FlexE(ref_pdb_file=ref_path)
            output = f.compare_with_ref(pdb_file=this_comp_file)
            create_result_obj(job, basename(this_comp_file), output)
        # after all comparison files have been processed
        job.status = Job.STATUS.done

    except Exception as e:
        error_message = str(e)
        logging.error(error_message)
        job.status = Job.STATUS.error
        job.error_message = error_message

    sleep(10.) # seconds
    job.save()
    rmtree(temp_dir)
    job.reference.delete()
    job.comparison.delete()
    return

def create_result_obj(job, filename, output):
    rmsd, energy_ref_to_pdb, energy_pdb_to_ref = output
    print job, filename, output
    r = Result.objects.create(job=job, rmsd=rmsd, name=filename,
                              energy_ref_to_pdb=energy_ref_to_pdb,
                              energy_pdb_to_ref=energy_pdb_to_ref)
    return
