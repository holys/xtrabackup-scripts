import subprocess
from xtrabackup.exception import CommandError


class CommandExecutor:

    def __init__(self, error_file_path):
        self.error_file_path = error_file_path

    def exec_command(self, command):
        with open(self.error_file_path, 'a+') as error_file:
            process = subprocess.Popen(command, stdout=error_file,
                                       stderr=subprocess.STDOUT)
            process.communicate()
            if process.returncode != 0:
                raise CommandError(command, process.returncode)

    def exec_filesystem_backup(self, user, password,
                               threads, backup_directory):
        command = [
            'innobackupex',
            '--user=' + user,
            '--parallel=' + threads,
            '--no-lock',
            '--no-timestamp',
            backup_directory]
        if password:
            command.append('--password=' + password)
        self.exec_command(command)

    def exec_incremental_backup(self, user, password,
                                threads, lsn, backup_directory):
        command = [
            'innobackupex',
            '--user=' + user,
            '--parallel=' + threads,
            '--incremental',
            '--incremental-lsn=' + lsn,
            '--no-lock',
            '--no-timestamp',
            backup_directory]
        if password:
            command.append('--password=' + password)
        self.exec_command(command)

    def exec_backup_preparation(self, backup_directory, redo_logs):
        command = [
            'innobackupex',
            '--apply-log',
            backup_directory]
        if redo_logs:
            command.append('--redo-only')
        self.exec_command(command)

    def exec_incremental_preparation(self, backup_directory,
                                     incremental_directory):
        command = [
            'innobackupex',
            '--apply-log',
            '--redo-only',
            '--incremental-dir=' + incremental_directory,
            backup_directory]
        self.exec_command(command)

    def exec_manage_service(self, service_name, action):
        command = ['/etc/init.d/' + service_name, action]
        self.exec_command(command)

    def exec_chown(self, user, group, directory_path):
        command = ['/bin/chown', '-R', user + ':' + group, directory_path]
        self.exec_command(command)

    def create_archive(self, directory, archive_path):
        command = [
            'tar',
            'cpvzf',
            archive_path,
            '-C',
            directory, '.']
        self.exec_command(command)

    def extract_archive(self, archive_path, destination_path):
        command = [
            'tar',
            'xpvzf',
            archive_path,
            '-C',
            destination_path]
        self.exec_command(command)
