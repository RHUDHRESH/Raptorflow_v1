# 💾 Backup & Disaster Recovery Guide

Comprehensive backup and disaster recovery procedures for RaptorFlow 2.0 production environment.

---

## 🎯 Overview

This guide covers:
- Automated backup configuration
- Manual backup procedures
- Backup verification
- Disaster recovery testing
- Recovery time objectives (RTO)
- Recovery point objectives (RPO)
- Disaster scenarios and procedures

---

## 📊 Backup Strategy

### Backup Objectives

```
Recovery Point Objective (RPO): 5 minutes
- Maximum data loss tolerance: 5 minutes of transactions
- Backup frequency: Every 5 minutes for critical data

Recovery Time Objective (RTO): 1 hour
- Maximum downtime tolerance: 1 hour
- Target restoration time: < 30 minutes

Retention Policy:
- Daily backups: 30 days retention
- Weekly backups: 12 weeks retention
- Monthly backups: 12 months retention
- Yearly backups: 7 years retention (compliance)
```

### Backup Architecture

```
┌─────────────────────────────────────────────────────┐
│           Production Database (RDS)                  │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌──────▼──────┐
    │ Automated│          │   Manual    │
    │ Snapshot │          │  Snapshot   │
    │  (daily) │          │  (as-needed)│
    └────┬─────┘          └──────┬──────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼─────────┐
              │   S3 Storage   │
              │  (encrypted)   │
              └────────────────┘
                     │
         ┌───────────┴──────────────┐
         │                          │
    ┌────▼────┐          ┌──────────▼──┐
    │ Local    │          │   Cross-    │
    │ Region   │          │   Region    │
    │ Backup   │          │   Replica   │
    └──────────┘          └─────────────┘
```

---

## 🔧 Database Backup Configuration

### 1. Automated RDS Backups

```bash
# 1a. Configure automated backups
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --backup-retention-period 30 \
  --preferred-backup-window "02:00-03:00" \
  --preferred-maintenance-window "sun:03:00-sun:04:00" \
  --enable-iam-database-authentication \
  --apply-immediately

# 1b. Verify backup configuration
aws rds describe-db-instances \
  --db-instance-identifier raptorflow-prod \
  --query 'DBInstances[0].[
    BackupRetentionPeriod,
    PreferredBackupWindow,
    PreferredMaintenanceWindow,
    StorageEncrypted
  ]'

# Expected output:
# [30, "02:00-03:00", "sun:03:00-sun:04:00", true]

# 1c. Enable backup encryption
aws rds modify-db-instance \
  --db-instance-identifier raptorflow-prod \
  --storage-encrypted \
  --kms-key-id arn:aws:kms:us-east-1:ACCOUNT:key/KEY_ID \
  --apply-immediately
```

### 2. Backup Snapshots

```bash
# 2a. List available backups
aws rds describe-db-snapshots \
  --db-instance-identifier raptorflow-prod

# Expected output: List of automated snapshots
# Example:
# raptorflow-prod-automated-2024-01-15-02:00
# raptorflow-prod-automated-2024-01-14-02:00
# etc.

# 2b. Create manual snapshot (before major changes)
aws rds create-db-snapshot \
  --db-instance-identifier raptorflow-prod \
  --db-snapshot-identifier raptorflow-prod-manual-2024-01-15

# Wait for snapshot to complete
aws rds wait db-snapshot-available \
  --db-snapshot-identifier raptorflow-prod-manual-2024-01-15

# 2c. Copy snapshot to another region (for disaster recovery)
aws rds copy-db-snapshot \
  --source-db-snapshot-identifier "arn:aws:rds:us-east-1:ACCOUNT:snapshot:raptorflow-prod-manual-2024-01-15" \
  --target-db-snapshot-identifier raptorflow-prod-backup-us-west-2 \
  --region us-west-2

# 2d. Verify snapshot
aws rds describe-db-snapshots \
  --db-snapshot-identifier raptorflow-prod-manual-2024-01-15 \
  --query 'DBSnapshots[0].Status'

# Expected: available
```

### 3. Automated Snapshot Management

```bash
# Create Lambda function for automated backup management
cat > lambda-backup-retention.js << 'EOF'
const AWS = require('aws-sdk');
const rds = new AWS.RDS();

const RETENTION_DAYS = 30;
const REGION = 'us-east-1';

exports.handler = async (event) => {
  try {
    // List all manual snapshots
    const snapshots = await rds.describeDBSnapshots({
      SnapshotType: 'manual',
      DBInstanceIdentifier: 'raptorflow-prod'
    }).promise();

    const now = new Date();
    const cutoff = new Date(now.getTime() - RETENTION_DAYS * 24 * 60 * 60 * 1000);

    // Delete old snapshots
    for (const snapshot of snapshots.DBSnapshots) {
      if (new Date(snapshot.SnapshotCreateTime) < cutoff) {
        console.log(`Deleting old snapshot: ${snapshot.DBSnapshotIdentifier}`);
        await rds.deleteDBSnapshot({
          DBSnapshotIdentifier: snapshot.DBSnapshotIdentifier,
          SkipFinalSnapshot: true
        }).promise();
      }
    }

    return {
      statusCode: 200,
      body: JSON.stringify('Backup cleanup completed')
    };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
EOF

# Deploy Lambda (using SAM or CloudFormation)
# Schedule with EventBridge: Once daily at 01:00 UTC
```

---

## 📦 Data Export & Long-Term Storage

### 1. Export to S3

```bash
# 1a. Create S3 bucket for long-term backup storage
aws s3api create-bucket \
  --bucket raptorflow-backups-export \
  --region us-east-1

# 1b. Enable versioning
aws s3api put-bucket-versioning \
  --bucket raptorflow-backups-export \
  --versioning-configuration Status=Enabled

# 1c. Enable encryption
aws s3api put-bucket-encryption \
  --bucket raptorflow-backups-export \
  --server-side-encryption-configuration '
  {
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

# 1d. Start export task
aws rds start-export-task \
  --export-task-identifier raptorflow-export-2024-01 \
  --source-arn "arn:aws:rds:us-east-1:ACCOUNT:db:raptorflow-prod" \
  --s3-bucket-name raptorflow-backups-export \
  --s3-prefix "monthly/2024-01/" \
  --iam-role-arn "arn:aws:iam::ACCOUNT:role/RDSExportRole"

# 1e. Monitor export progress
aws rds describe-export-tasks \
  --export-task-identifier raptorflow-export-2024-01 \
  --query 'ExportTasks[0].Status'

# Expected: COMPLETE (takes 10-30 minutes depending on database size)

# 1f. Verify export in S3
aws s3 ls s3://raptorflow-backups-export/monthly/2024-01/

# Expected: Parquet files for each table
```

### 2. Cross-Region Backup

```bash
# 2a. Create read replica in another region (automatic backups)
aws rds create-db-instance-read-replica \
  --db-instance-identifier raptorflow-prod-backup-us-west-2 \
  --source-db-instance-identifier raptorflow-prod \
  --db-instance-class db.t3.small \
  --storage-type gp3 \
  --publicly-accessible false \
  --region us-west-2

# 2b. Wait for replica creation (5-10 minutes)
aws rds wait db-instance-available \
  --db-instance-identifier raptorflow-prod-backup-us-west-2 \
  --region us-west-2

# 2c. Verify replica
aws rds describe-db-instances \
  --db-instance-identifier raptorflow-prod-backup-us-west-2 \
  --region us-west-2 \
  --query 'DBInstances[0].DBInstanceStatus'

# Expected: available
```

---

## 🧪 Backup Verification

### 1. Snapshot Verification

```bash
# 1a. List latest snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier raptorflow-prod \
  --query 'sort_by(DBSnapshots, &SnapshotCreateTime)[-5:].{
    Identifier: DBSnapshotIdentifier,
    Created: SnapshotCreateTime,
    Status: Status,
    Size: AllocatedStorage
  }' \
  --output table

# 1b. Test restore from snapshot (test environment)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-test-restore \
  --db-snapshot-identifier raptorflow-prod-manual-2024-01-15 \
  --db-instance-class db.t3.small \
  --no-publicly-accessible

# 1c. Wait for restore completion
aws rds wait db-instance-available \
  --db-instance-identifier raptorflow-prod-test-restore

# 1d. Verify restored database
# Connect and query:
psql -h $RESTORED_ENDPOINT -U postgres -d raptorflow -c "SELECT COUNT(*) FROM users"

# Expected: Row count should match production

# 1e. Delete test restore
aws rds delete-db-instance \
  --db-instance-identifier raptorflow-prod-test-restore \
  --skip-final-snapshot
```

### 2. Data Consistency Checks

```bash
# 2a. Generate checksum of production database
PROD_CHECKSUM=$(psql -h $PROD_HOST -U postgres -d raptorflow -t -c "
  SELECT md5(string_agg(t::text, '' ORDER BY t::text))
  FROM (
    SELECT row_to_json(t) t FROM (
      SELECT * FROM users ORDER BY id
    ) t
  ) AS sub
")

# 2b. Generate checksum from restored backup
BACKUP_CHECKSUM=$(psql -h $BACKUP_HOST -U postgres -d raptorflow -t -c "
  SELECT md5(string_agg(t::text, '' ORDER BY t::text))
  FROM (
    SELECT row_to_json(t) t FROM (
      SELECT * FROM users ORDER BY id
    ) t
  ) AS sub
")

# 2c. Compare checksums
if [ "$PROD_CHECKSUM" == "$BACKUP_CHECKSUM" ]; then
  echo "✅ Backup is consistent with production"
else
  echo "❌ BACKUP INTEGRITY ERROR!"
  exit 1
fi
```

### 3. Backup Audit Log

```bash
# Create audit log for all backups
cat > backup-audit.log << 'EOF'
DATE,SNAPSHOT_ID,TYPE,STATUS,SIZE_GB,VERIFIED,NOTES
2024-01-15,raptorflow-prod-manual-2024-01-15,manual,available,45.2,yes,Pre-deployment backup
2024-01-15,raptorflow-prod-automated-2024-01-15-02:00,automated,available,45.1,yes,Automated daily
2024-01-14,raptorflow-prod-automated-2024-01-14-02:00,automated,available,45.0,yes,Automated daily
EOF

# Store in S3 for compliance
aws s3 cp backup-audit.log \
  s3://raptorflow-backups-export/audit/backup-audit.log
```

---

## 🚨 Disaster Recovery Procedures

### Scenario 1: Single Table Corruption

```bash
# 1. Identify problem
# Users report data inconsistency in 'strategies' table

# 2. Create point-in-time recovery
RECOVERY_TIME=$(date -d "30 minutes ago" -u +"%Y-%m-%dT%H:%M:%SZ")

aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier raptorflow-prod \
  --target-db-instance-identifier raptorflow-prod-recovery \
  --restore-time $RECOVERY_TIME

# 3. Wait for recovery
aws rds wait db-instance-available \
  --db-instance-identifier raptorflow-prod-recovery

# 4. Export corrupted table from recovery instance
pg_dump -h $RECOVERY_HOST -U postgres -d raptorflow \
  -t strategies > strategies-backup.sql

# 5. Restore table to production
psql -h $PROD_HOST -U postgres -d raptorflow << 'EOF'
BEGIN;
DELETE FROM strategies;
\i strategies-backup.sql
COMMIT;
EOF

# 6. Verify recovery
psql -h $PROD_HOST -U postgres -d raptorflow -c \
  "SELECT COUNT(*) FROM strategies"

# 7. Clean up recovery instance
aws rds delete-db-instance \
  --db-instance-identifier raptorflow-prod-recovery \
  --skip-final-snapshot
```

### Scenario 2: Complete Database Failure

```bash
# SEVERITY: CRITICAL
# RTO: < 1 hour
# RPO: < 5 minutes

# 1. IMMEDIATE: Alert team and activate incident response
# - Post in #incidents: "🚨 Database failure - activating recovery"
# - Page on-call DBA
# - Start incident timer

# 2. Prepare recovery infrastructure (2 min)
# Launch new RDS instance in same region
aws rds create-db-instance \
  --db-instance-identifier raptorflow-prod-recovery \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --allocated-storage 100 \
  --storage-type gp3 \
  --backup-retention-period 30 \
  --multi-az

# 3. Restore from latest snapshot (5-15 min depending on size)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-new \
  --db-snapshot-identifier raptorflow-prod-automated-2024-01-15-02:00 \
  --db-instance-class db.t3.medium

# 4. Wait for restoration
aws rds wait db-instance-available \
  --db-instance-identifier raptorflow-prod-new

# 5. Update application connection string
# Update environment variable: DATABASE_URL
# Point to new instance endpoint

# 6. Perform sanity checks (5 min)
psql -h $NEW_HOST -U postgres -d raptorflow -c "
  SELECT COUNT(*) as user_count FROM users;
  SELECT COUNT(*) as strategy_count FROM strategies;
"

# 7. Restart application (2 min)
# Clear connection pools and restart

# 8. Verify application health (5 min)
curl -f https://raptorflow.com/health

# 9. Monitor closely for 1 hour

# 10. Document incident
# - Timeline of failure
# - Root cause analysis
# - Lessons learned
# - Preventive measures
```

### Scenario 3: Regional Outage

```bash
# SEVERITY: CRITICAL
# RTO: < 30 minutes
# RPO: < 5 minutes (read replica in another region)

# 1. IMMEDIATE: Verify outage scope
aws ec2 describe-regions \
  --region-names us-east-1 \
  --query 'Regions[0].{RegionName,OptInStatus}'

# 2. Switch to backup region (using read replica)
# Promote read replica to standalone instance
aws rds promote-read-replica \
  --db-instance-identifier raptorflow-prod-backup-us-west-2 \
  --region us-west-2

# 3. Update DNS to point to us-west-2
# Using Route 53 failover
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch '{
    "Changes": [{
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "api.raptorflow.com",
        "Type": "CNAME",
        "TTL": 60,
        "ResourceRecords": [{"Value": "us-west-2-endpoint.rds.amazonaws.com"}]
      }
    }]
  }'

# 4. Update application configuration
# Point to us-west-2 database
# Deploy config change

# 5. Verify traffic reaching us-west-2
tail -f /var/log/nginx/access.log | grep us-west-2

# 6. Monitor us-west-2 instance
watch -n 5 'aws cloudwatch get-metric-statistics \
  --namespace AWS/RDS \
  --metric-name DatabaseConnections \
  --dimensions Name=DBInstanceIdentifier,Value=raptorflow-prod-backup-us-west-2 \
  --region us-west-2 \
  --start-time $(date -u -d "5 minutes ago" +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 60 \
  --statistics Average'

# 7. Once us-east-1 recovers
# Sync data from us-west-2 back to us-east-1
# Set up replication again
# Update DNS back to us-east-1
```

### Scenario 4: Ransomware / Data Breach

```bash
# SEVERITY: CRITICAL
# RTO: < 2 hours
# RPO: < 1 hour

# 1. IMMEDIATE: Isolate affected systems
# Stop all database connections from application

# 2. Preserve forensics
# Copy current database snapshot for investigation
aws rds create-db-snapshot \
  --db-instance-identifier raptorflow-prod \
  --db-snapshot-identifier raptorflow-prod-forensics-2024-01-15

# 3. Restore clean backup (from before attack)
# Identify last known good backup (check CloudTrail timestamps)
aws rds describe-db-snapshots \
  --db-instance-identifier raptorflow-prod \
  --query 'DBSnapshots[?SnapshotCreateTime<`2024-01-15T10:00:00Z`] | sort_by(@, &SnapshotCreateTime)[-1]'

# 4. Restore to new instance
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier raptorflow-prod-recovery \
  --db-snapshot-identifier [CLEAN_SNAPSHOT]

# 5. Verify data integrity
# Run consistency checks
# Scan for malicious modifications

# 6. Swap instances (promote recovery as primary)
# Update application DNS
# Enable read-only mode until verification complete

# 7. Notify users
# Send security alert
# Recommend password reset
# Advise monitoring for fraud

# 8. Post-incident
# Root cause analysis
# Update security policies
# Implement additional monitoring
```

---

## 📋 Backup Checklist

### Daily Tasks
```
☐ Verify automated backup completed
☐ Check backup size (should be stable)
☐ Monitor backup duration (should be < 1 hour)
☐ Check for backup errors in logs
```

### Weekly Tasks
```
☐ Test restore from latest snapshot
☐ Verify data consistency
☐ Review backup audit log
☐ Check S3 export bucket
```

### Monthly Tasks
```
☐ Test complete disaster recovery scenario
☐ Review and update RPO/RTO
☐ Audit backup retention policies
☐ Document any issues found
☐ Update recovery runbooks
```

### Quarterly Tasks
```
☐ Test cross-region failover
☐ Performance test recovery instances
☐ Update disaster recovery procedures
☐ Train team on recovery procedures
☐ Review backup architecture
```

---

## 🔗 Related Documentation

- **Deployment Guide:** `DEPLOYMENT_GUIDE.md`
- **Deployment Runbook:** `DEPLOYMENT_RUNBOOK.md`
- **Security Hardening:** `SECURITY_HARDENING.md`
- **Monitoring Setup:** `MONITORING_SETUP.md`

---

## 📞 Recovery Support

For disaster recovery assistance:
1. Page on-call DBA
2. Contact AWS Support (if enterprise support)
3. Check AWS Service Health Dashboard
4. Review this runbook section for scenario

---

**Last Updated:** Phase 5 Week 3
**Next Review:** Post-deployment testing
**RTO/RPO Review:** Quarterly
