import paramiko
import socket
import logging
from typing import Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSHConnectionError(Exception):
    """Custom exception for SSH connection errors"""
    pass

def establish_ssh_connection(
    host: str,
    username: str,
    password: Optional[str] = None,
    key_filename: Optional[str] = None
) -> Union[paramiko.SSHClient, None]:
    """
    Establishes an SSH connection to a remote host.
    
    Args:
        host (str): The hostname or IP address to connect to
        username (str): The username for authentication
        password (str, optional): The password for password-based authentication
        key_filename (str, optional): Path to the private key file for key-based authentication
        
    Returns:
        paramiko.SSHClient: The connected SSH client object
        
    Raises:
        SSHConnectionError: If connection fails for any reason
    """
    try:
        # Input validation
        if not host or not username:
            raise SSHConnectionError("Host and username are required")
            
        if not password and not key_filename:
            raise SSHConnectionError("Either password or key file is required")
            
        # Create a new SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Attempt connection
        logger.info(f"Attempting SSH connection to {host} as {username}")
        
        connect_kwargs = {
            "hostname": host,
            "username": username,
            "timeout": 10
        }
        
        if password:
            connect_kwargs["password"] = password
        if key_filename:
            connect_kwargs["key_filename"] = key_filename
            
        client.connect(**connect_kwargs)
        
        logger.info(f"Successfully established SSH connection to {host}")
        return client
        
    except paramiko.AuthenticationException:
        logger.error(f"Authentication failed for {username}@{host}")
        raise SSHConnectionError("Authentication failed. Please check your credentials.")
        
    except paramiko.SSHException as e:
        logger.error(f"SSH exception occurred: {str(e)}")
        raise SSHConnectionError(f"SSH error: {str(e)}")
        
    except socket.error as e:
        logger.error(f"Socket error occurred: {str(e)}")
        raise SSHConnectionError(f"Network error: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise SSHConnectionError(f"Unexpected error: {str(e)}")

def close_ssh_connection(client: paramiko.SSHClient) -> None:
    """
    Safely closes an SSH connection.
    
    Args:
        client (paramiko.SSHClient): The SSH client to close
    """
    try:
        if client:
            client.close()
            logger.info("SSH connection closed successfully")
    except Exception as e:
        logger.error(f"Error closing SSH connection: {str(e)}")
