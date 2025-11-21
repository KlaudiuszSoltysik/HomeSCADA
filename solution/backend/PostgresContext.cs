using Microsoft.EntityFrameworkCore;

namespace backend;

public class PostgresContext(DbContextOptions<PostgresContext> options) : DbContext(options)
{
    // public DbSet<User> Users { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);
    }
}