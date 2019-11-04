# install and configure a bpf2graphite service
## installs python script into /opt/bpf2graphite and allows overrides for port and graphite server
## bpf2graphite_location <string> - location to install to. defaults to /opt/bpf2graphite
## bpf2graphite_server <string> - server listening for graphite. defaults to localhost
## bpf2graphite_port <string> - port listening for graphite. defaults to 2003
## bpf2graphite_servicename <string> - name of the systemd service

class bpf2graphite {
  $bpf2graphite_location = '/opt/bpf2graphite'
  $bpf2graphite_server = 'localhost'
  $bpf2graphite_port = '2003'
  $bpf2graphite_servicename = 'bpf2graphite'

  package {'bpftrace':
        ensure => 'installed'
  }


  file { $bpf2graphite_location:
        ensure => 'directory'
  }

  file { "${bpf2graphite_location}/bpf2graphite.py":
        ensure => 'present',
        source => 'puppet:///modules/bpf2graphite/bpf2graphite.py',
        mode   => '0744'
  }

  file { "${bpf2graphite_location}/cpu_latency.bt":
        ensure => 'present',
        source => 'puppet:///modules/bpf2graphite/cpu_latency.bt',
        mode   => '0744'
  }

  file { "/etc/systemd/system/${bpf2graphite_servicename}.service":
        ensure  => 'present',
        content => template('bpf2graphite/bpf2graphite.service.erb')
  }
  service { 'bpf2graphite':
        ensure    => 'running',
        enable    => true,
        provider  => 'systemd',
        subscribe => File["${bpf2graphite_location}/bpf2graphite.py"]
  }

}
