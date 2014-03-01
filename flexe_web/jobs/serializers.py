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
        fields = ('id', 'url', 'title', 'status', 'owner', 'reference', 'comparison',
                  'result')
        read_only_fields = ('status',)

    def validate_reference(self, attrs, source):
        """
        Check that reference file is a pdb file.
        """
        uploaded_file = attrs[source]
        if uploaded_file.name.endswith('.pdb'):
            return attrs
        else:
            raise serializers.ValidationError('Reference file must be a .pdb file.')

    def validate_comparison(self, attrs, source):
        """
        Check that comparison file is a pdb file or a zip file (of pdbs).
        """
        uploaded_file = attrs[source]
        if uploaded_file.name.endswith('.pdb'):
            return attrs
        elif uploaded_file.name.endswith('.zip'):
            return attrs
        else:
            raise serializers.ValidationError('Comparison file must be a .pdb file or .zip file.')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    jobs = serializers.HyperlinkedRelatedField(many=True, view_name='job-detail')

    class Meta:
        model = User
        fields = ('url', 'username', 'jobs')
