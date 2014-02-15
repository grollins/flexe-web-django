from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Job, Result


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result


class JobSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.Field(source='owner.username')
    result = ResultSerializer(read_only=True)

    class Meta:
        model = Job
        fields = ('title', 'status', 'owner', 'reference_file', 'comparison_file',
                  'result')
        read_only_fields = ('status',)

    def validate_reference_file(self, attrs, source):
        """
        Check that reference file is a pdb file.
        """
        uploaded_file = attrs[source]
        if uploaded_file.name.endswith('.pdb'):
            return attrs
        else:
            raise serializers.ValidationError('Reference file must be a .pdb file.')

    def validate_topology(self, attrs, source):
        """
        Check that comparison file is a pdb file or a zip of pdbs.
        """
        uploaded_file = attrs[source]
        if uploaded_file.name.endswith('.pdb'):
            return attrs
        else:
            raise serializers.ValidationError('Comparison file must be a .pdb file.')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    jobs = serializers.HyperlinkedRelatedField(many=True, view_name='job-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'jobs')
