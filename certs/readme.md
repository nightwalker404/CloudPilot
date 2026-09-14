# Incus Certificate Setup

The application uses certificates to connect to the Incus API.

The certificates must be placed inside the `certs` folder:

```text
certs/
├── client.crt
├── client.key
└── server.crt
```

## 1. Create client certificate

On the machine where the application runs:

```bash
incus remote generate-certificate
```

This creates:

```text
~/.config/incus/client.crt
~/.config/incus/client.key
```

## 2. Allow the certificate in Incus

Add the client certificate to Incus:

```bash
incus config trust add-certificate ~/.config/incus/client.crt
```

Check:

```bash
incus config trust list
```

You should see the certificate listed as:

```text
TYPE: client
```

## 3. Copy certificates into the project

Copy the client certificate:

```bash
cp ~/.config/incus/client.crt certs/
```

Copy the client private key:

```bash
cp ~/.config/incus/client.key certs/
```

Copy the Incus server certificate:

```bash
sudo cp /var/lib/incus/server.crt certs/
```

The final folder should be:

```text
certs/
├── client.crt
├── client.key
└── server.crt
```

## 4. Protect the private key

The `client.key` file is sensitive. Do not share it.

Set permissions:

```bash
chmod 600 certs/client.key
```

## Certificate purpose

| File         | Purpose                                                                 |
| ------------ | ----------------------------------------------------------------------- |
| `client.crt` | Identifies the application to Incus                                     |
| `client.key` | Private key used with the client certificate                            |
| `server.crt` | Verifies that the application is connecting to the correct Incus server |

After placing these files in `certs/`, the application can authenticate with the Incus API.
