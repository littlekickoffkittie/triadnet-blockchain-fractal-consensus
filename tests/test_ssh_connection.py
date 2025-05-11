import unittest
from unittest.mock import MagicMock, patch
from blockchain.network.ssh_connector import establish_ssh_connection, close_ssh_connection, SSHConnectionError

class TestSSHConnection(unittest.TestCase):
    @patch('paramiko.SSHClient')
    def test_successful_connection(self, mock_ssh):
        # Setup mock
        mock_client = MagicMock()
        mock_ssh.return_value = mock_client
        
        # Test connection with password
        client = establish_ssh_connection(
            host="192.168.1.164",
            username="amy",
            password="test_password"
        )
        
        # Verify
        mock_client.connect.assert_called_once_with(
            hostname="192.168.1.164",
            username="amy",
            password="test_password",
            timeout=10
        )
        self.assertEqual(client, mock_client)
        
    @patch('paramiko.SSHClient')
    def test_authentication_failure(self, mock_ssh):
        # Setup mock
        mock_client = MagicMock()
        mock_ssh.return_value = mock_client
        mock_client.connect.side_effect = SSHConnectionError("Authentication failed")
        
        # Test
        with self.assertRaises(SSHConnectionError) as context:
            establish_ssh_connection(
                host="192.168.1.164",
                username="amy",
                password="wrong_password"
            )
        
        self.assertIn("Authentication failed", str(context.exception))
        
    def test_invalid_parameters(self):
        # Test missing host
        with self.assertRaises(SSHConnectionError) as context:
            establish_ssh_connection(
                host="",
                username="amy",
                password="test_password"
            )
        self.assertIn("Host and username are required", str(context.exception))
        
        # Test missing username
        with self.assertRaises(SSHConnectionError) as context:
            establish_ssh_connection(
                host="192.168.1.164",
                username="",
                password="test_password"
            )
        self.assertIn("Host and username are required", str(context.exception))
        
        # Test missing credentials
        with self.assertRaises(SSHConnectionError) as context:
            establish_ssh_connection(
                host="192.168.1.164",
                username="amy"
            )
        self.assertIn("Either password or key file is required", str(context.exception))
    
    @patch('paramiko.SSHClient')
    def test_close_connection(self, mock_ssh):
        # Setup mock
        mock_client = MagicMock()
        mock_ssh.return_value = mock_client
        
        # Test close
        close_ssh_connection(mock_client)
        
        # Verify
        mock_client.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
